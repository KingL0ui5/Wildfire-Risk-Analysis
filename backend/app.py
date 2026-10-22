import numpy as np
from flask import Flask, request, jsonify
from helpers.converter import csv_to_geojson
import json
import csv
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
    """Rank-based percentile normalisation to a 0-100 scale (robust to heavy tails)."""
    arr = np.asarray(values, dtype=float)
    ranks = arr.argsort().argsort()
    return 100.0 * ranks / max(len(arr) - 1, 1)


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


def build_risk_surface(csv_path, cell=0.1, power=2):
    """
    Interpolate point risk values onto a regular grid using inverse
    distance weighting (IDW), returned as a GeoJSON FeatureCollection
    of grid-cell polygons.
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

    lats, lons = np.asarray(lats), np.asarray(lons)
    risks = normalise_risks(risks)
    lon_edges = np.arange(lons.min() - cell, lons.max() + 2 * cell, cell)
    lat_edges = np.arange(lats.min() - cell, lats.max() + 2 * cell, cell)
    lon_c = (lon_edges[:-1] + lon_edges[1:]) / 2
    lat_c = (lat_edges[:-1] + lat_edges[1:]) / 2

    glon, glat = np.meshgrid(lon_c, lat_c)
    d2 = (glon[..., None] - lons) ** 2 + (glat[..., None] - lats) ** 2
    w = 1.0 / np.maximum(d2, 1e-6) ** (power / 2)
    grid = (w * risks).sum(axis=-1) / w.sum(axis=-1)

    features = []
    for i in range(len(lat_c)):
        for j in range(len(lon_c)):
            x0, x1 = lon_edges[j], lon_edges[j + 1]
            y0, y1 = lat_edges[i], lat_edges[i + 1]
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
