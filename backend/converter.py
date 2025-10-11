import csv
import json
import sys
from pathlib import Path


def csv_to_geojson(csv_path, geojson_path):
    """
    Convert a CSV file to a GeoJSON file.
    Inputs:
        input.csv filepath, output.geojson filepath

    Expected CSV columns:
        Risk, HumanOrLightning, Lat_DD, Long_DD, Ign_DateTime
    """
    features = []

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row["Lat_DD"])
                lon = float(row["Long_DD"])
                risk = float(row["Risk"])
                cause = row["HumanOrLightning"].strip()
                dt = row["Ign_DateTime"].strip()
            except (KeyError, ValueError) as e:
                print(f"Skipping row due to error: {e}")
                continue

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "cause": cause,
                    "risk": risk,
                    "datetime": dt
                }
            }
            features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"GeoJSON file saved to: {geojson_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_geojson.py input.csv output.geojson")
        sys.exit(1)

    input_csv = Path(sys.argv[1])
    output_geojson = Path(sys.argv[2])

    if not input_csv.exists():
        print(f"Input file not found: {input_csv}")
        sys.exit(1)

    csv_to_geojson(input_csv, output_geojson)


