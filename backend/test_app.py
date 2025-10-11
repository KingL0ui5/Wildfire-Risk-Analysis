from flask import Flask, jsonify, request
import logging

logging.basicConfig(
        filename='/home/linux1/api_requests.log',       # log file
    level=logging.INFO,                # log all INFO-level messages
    format='%(asctime)s %(levelname)s: %(message)s'
)

print("Python is active")

app = Flask(__name__)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.route("/data.geojson")
def get_data():
    # Example: generate or load a GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {"name": "Center"}}
        ]
    }
    logging.info("Returned GeoJSON data")
    return jsonify(geojson_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

