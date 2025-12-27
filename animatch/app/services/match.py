import json
from pathlib import Path

def load_characters():
    data_path = Path(__file__).resolve().parents[1] / "data" / "anime_vectors.json" #fetchs and appends anime vectors 
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)
