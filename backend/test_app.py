from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/data.geojson")
def get_data():
    # Example: generate or load a GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {"name": "Center"}}
        ]
    }
    return jsonify(geojson_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

