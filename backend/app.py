import numpy as np
from flask import Flask, request, jsonify, Response
from helpers.converter import csv_to_geojson
import json
import csv
import io
from PIL import Image
from flask_cors import CORS


# Create the Flask app
app = Flask(__name__)
CORS(app)

# Path to model file
# MODEL_PATH = os.environ.get("MODEL_PATH", "models/wildfire_model.pkl")

# # Load model on startup
# try:
#     model = joblib.load(MODEL_PATH)
#     print(f"✅ Model loaded from {MODEL_PATH}")
# except Exception as e:
#     print(f"❌ Failed to load model from {MODEL_PATH}: {e}")
#     model = None

@app.route("/")
def home():
    return jsonify({"message": "🔥 Wildfire Forecast API is running. \n(home directory accessed)"})

def normalise_risks(values):
    """Log-scaled min-max normalisation to a 0-100 scale (robust to heavy tails)."""
    arr = np.asarray(values, dtype=float)
    logs = np.log10(arr + 1)
    lo, hi = logs.min(), logs.max()
    return 100.0 * (logs - lo) / max(hi - lo, 1e-9)


@app.route("/predict")
def predict():
    """
    Return risk predictions in geojson format
    """

    # randomise data here
    csv_to_geojson("helpers/data/input.csv", "helpers/data/output.geojson")
    with open("helpers/data/output.geojson", encoding="utf-8") as f:
        geojson_data = json.load(f)

    features = geojson_data.get("features", [])
    normed = normalise_risks([f["properties"]["risk"] for f in features])
    for feature, score in zip(features, normed):
        feature["properties"]["raw_risk"] = feature["properties"]["risk"]
        feature["properties"]["risk"] = round(float(score), 2)

    return jsonify(geojson_data)


def build_risk_surface(csv_path, cell=0.1, sigma=0.25):
    """
    Build a severity-weighted fire-density surface on a regular grid,
    returned as a GeoJSON FeatureCollection of grid-cell polygons.
    Each cell scores the amount of nearby fire activity (Gaussian kernel),
    weighted by log severity, then log-normalised to 0-100.
    """
    lats, lons, risks = [], [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                lats.append(float(row["Lat_DD"]))
                lons.append(float(row["Long_DD"]))
                risks.append(float(row["Risk"]))
            except (KeyError, ValueError):
                continue

    lats, lons, risks = np.asarray(lats), np.asarray(lons), np.asarray(risks)
    lon_edges = np.arange(lons.min() - cell, lons.max() + 2 * cell, cell)
    lat_edges = np.arange(lats.min() - cell, lats.max() + 2 * cell, cell)
    lon_c = (lon_edges[:-1] + lon_edges[1:]) / 2
    lat_c = (lat_edges[:-1] + lat_edges[1:]) / 2

    glon, glat = np.meshgrid(lon_c, lat_c)
    d2 = (glon[..., None] - lons) ** 2 + (glat[..., None] - lats) ** 2
    w = np.exp(-d2 / (2 * sigma ** 2))
    density = (w * (1 + np.log10(1 + risks))).sum(axis=-1)
    grid = 100.0 * np.log1p(density) / max(np.log1p(density.max()), 1e-9)

    # Slightly overlap cells to avoid hairline seams when rendered as fills
    pad = cell * 0.05
    features = []
    for i in range(len(lat_c)):
        for j in range(len(lon_c)):
            x0, x1 = lon_edges[j] - pad, lon_edges[j + 1] + pad
            y0, y1 = lat_edges[i] - pad, lat_edges[i + 1] + pad
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]],
                },
                "properties": {"risk": round(float(grid[i, j]), 2)},
            })

    return {"type": "FeatureCollection", "features": features}


_surface_cache = None


@app.route("/risk-surface")
def risk_surface():
    """
    Return an IDW-interpolated continuous risk surface as GeoJSON grid polygons.
    """
    global _surface_cache
    if _surface_cache is None:
        _surface_cache = build_risk_surface("helpers/data/input.csv")
    return jsonify(_surface_cache)


def _colormap(vals):
    """Map 0-100 risk values to green->yellow->orange->red RGB channels."""
    stops = np.array([0, 35, 55, 70, 85, 100])
    reds = np.array([0, 170, 255, 255, 220, 200])
    greens = np.array([180, 220, 215, 140, 60, 0])
    blues = np.array([0, 0, 0, 0, 40, 0])
    return (np.interp(vals, stops, reds),
            np.interp(vals, stops, greens),
            np.interp(vals, stops, blues))


def build_risk_image(csv_path, cell=0.02, sigma=0.1):
    """
    Render the severity-weighted fire-density surface as a smooth RGBA PNG
    plus its geographic bounds, for use as a map image overlay.
    """
    lats, lons, risks = [], [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                lats.append(float(row["Lat_DD"]))
                lons.append(float(row["Long_DD"]))
                risks.append(float(row["Risk"]))
            except (KeyError, ValueError):
                continue

    lats, lons, risks = np.asarray(lats), np.asarray(lons), np.asarray(risks)
    lon_c = np.arange(lons.min() - cell, lons.max() + cell, cell)
    lat_c = np.arange(lats.min() - cell, lats.max() + cell, cell)
    severity = 1 + np.log10(1 + risks)

    rows = []
    for i in range(0, len(lat_c), 16):  # chunk rows to bound memory
        glat = lat_c[i:i + 16]
        d2 = (lon_c[None, :, None] - lons) ** 2 + (glat[:, None, None] - lats) ** 2
        rows.append((np.exp(-d2 / (2 * sigma ** 2)) * severity).sum(axis=-1))
    density = np.concatenate(rows, axis=0)
    grid = 100.0 * np.log1p(density) / max(np.log1p(density.max()), 1e-9)

    r, g, b = _colormap(grid)
    alpha = np.full_like(r, 160.0)
    rgba = np.flipud(np.stack([r, g, b, alpha], axis=-1)).astype(np.uint8)

    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG")
    bounds = {
        "west": float(lon_c[0] - cell / 2), "east": float(lon_c[-1] + cell / 2),
        "south": float(lat_c[0] - cell / 2), "north": float(lat_c[-1] + cell / 2),
    }
    return buf.getvalue(), bounds


_surface_image = None


def _surface_image_data():
    global _surface_image
    if _surface_image is None:
        _surface_image = build_risk_image("helpers/data/input.csv")
    return _surface_image


@app.route("/risk-surface.png")
def risk_surface_png():
    png, _ = _surface_image_data()
    return Response(png, mimetype="image/png")


@app.route("/risk-surface-bounds")
def risk_surface_bounds():
    _, bounds = _surface_image_data()
    return jsonify(bounds)

# @app.route("/predict", methods=["POST"])
# def predict():
#     """
#     Expects a JSON body like:
#     {
#         "features": [0.2, 1.5, 3.0, ...]
#     }
#     """
#     if model is None:
#         return jsonify({"error": "Model not loaded."}), 500

#     data = request.get_json()

#     if not data or "features" not in data:
#         return jsonify({"error": "Missing 'features' field."}), 400

#     try:
#         features = np.array(data["features"]).reshape(1, -1)
#         prediction = model.predict(features)
#         # Optional: if the model has probabilities
#         if hasattr(model, "predict_proba"):
#             proba = model.predict_proba(features).tolist()
#         else:
#             proba = None

#         return jsonify({
#             "prediction": prediction.tolist(),
#             "probabilities": proba
#         })
#     except Exception as e:
#         return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
