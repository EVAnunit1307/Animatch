import json
import math 
from pathlib import Path

def load_characters():
    data_path = Path(__file__).resolve().parents[1] / "data" / "anime_vectors.json" #fetchs and appends anime vectors 
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)
features = ["face_ratio", "eye_spacing", "eye_openness", "jaw_angle", "chin_ratio", "brow_height"]

def distance(user_vector, char_vector):
    total = 0.0
    for i in features:
        diffrence = user_vector[i] - char_vector[i]
        total += diffrence * diffrence
    return math.sqrt(total)
