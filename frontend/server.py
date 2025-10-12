from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow cross-origin during dev

@app.route('/predict')
def predict():
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-120.5, 43.8]},
                "properties": {"risk": 68, "name": "Corvallis"}
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-118.72, 42.49]},
                "properties": {"risk": 45, "name": "Southeast Oregon"}
            }
        ]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)
