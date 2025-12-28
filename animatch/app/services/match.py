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

def match_characters (user_features, top_k=3): #gets top 3 
    char = load_characters()
    scored = []

    for c in char:
        d = distance(user_features, c["vector"])
        sim = 1.0 / (1.0/d)
        scored.append((sim,c)) #ppends similarioty score and character 

    scored.sort(key=lambda x: x[0], reverse=True) #sorts by the first thing in tuple, from decending 

    results = []
    for sim, c in scored[:top_k]:#goes to scores takes top 3 
        results.append({
            "id": c["id"],
            "name": c["name"],
            "series": c["series"],
            "similarity": round(sim, 4),
            "vector": c["vector"]
        })

    return results


