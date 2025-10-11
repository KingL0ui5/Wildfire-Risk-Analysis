from flask import Flask, jsonify
import random

app = Flask(__name__)

# Rough Oregon bounding box
MIN_LAT, MAX_LAT = 41.9918, 46.2991
MIN_LON, MAX_LON = -124.7035, -116.4635

def generate_random_geojson(num_points=50):
    features = []
    for i in range(num_points):
        lat = random.uniform(MIN_LAT, MAX_LAT)
        lon = random.uniform(MIN_LON, MAX_LON)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {"id": i}
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.route("/data.geojson")
def get_data():
    """Return a fresh random GeoJSON every request"""
    return jsonify(generate_random_geojson())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

