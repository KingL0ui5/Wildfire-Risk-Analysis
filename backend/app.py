# import numpy as np
from flask import Flask, request, jsonify
from helpers.converter import csv_to_geojson
import json
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

@app.route("/predict")
def predict():
    """
    Return risk predictions in geojson format
    """

    # randomise data here
    csv_to_geojson("backend/helpers/data/input.csv", "backend/helpers/data/output.geojson")
    geojson_data = json.load("backend/helpers/data/output.geojson")

    return jsonify(geojson_data)

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
