from app import predict
import numpy as np
from flask import Flask, request, jsonify
from helpers.converter import csv_to_geojson
import json
import sys
from pathlib import Path

if __name__ == "__main__":
    input = Path(sys.argv[1])
    predict(input)

