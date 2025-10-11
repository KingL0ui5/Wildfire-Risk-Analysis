from flask import Flask, jsonify

app = Flask(__name__)       

@app.route("/data.geojson")
def get_data():
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
            "type": "Feature",
            "geometry": { "type": "Point", "coordinates": [-123.262, 44.564] },
            "properties": { "name": "Corvallis", "risk": 68 }
            }
        ]
    }       

    return jsonify(geojson_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

