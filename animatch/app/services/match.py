import json
import math 
from pathlib import Path

def load_characters():
    data_path = Path(__file__).resolve().parents[1] / "data" / "anime_vectors.json" #fetchs and appends anime vectors 
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)
features = ["face_ratio", "eye_spacing", "eye_openness", "jaw_angle", "chin_ratio", "brow_height"]

def compute_stats(characters):
    """Compute mean and std for each feature across the dataset."""
    stats = {f: {"mean": 0.0, "std": 0.0} for f in features}
    n = len(characters)
    if n == 0:
        return stats

    # mean
    for f in features:
        stats[f]["mean"] = sum(c["vector"][f] for c in characters) / n
    # std (sample)
    for f in features:
        mean = stats[f]["mean"]
        variance = sum((c["vector"][f] - mean) ** 2 for c in characters) / max(n - 1, 1)
        stats[f]["std"] = math.sqrt(variance)
    return stats

def normalize(vec, stats):
    """Z-score normalize a vector using provided stats."""
    out = {}
    for f in features:
        std = stats[f]["std"]
        if std == 0:
            out[f] = 0.0
        else:
            out[f] = (vec[f] - stats[f]["mean"]) / std
    return out

def distance(user_vector, char_vector):
    total = 0.0
    for i in features:
        diffrence = user_vector[i] - char_vector[i]
        total += diffrence * diffrence
    return math.sqrt(total)

def match_characters (user_features, top_k=3): #gets top 3 
    char = load_characters()
    stats = compute_stats(char)
    user_norm = normalize(user_features, stats)
    scored = []

    for c in char:
        c_norm = normalize(c["vector"], stats)
        d = distance(user_norm, c_norm)
        sim = 1.0 / (1.0 + d)  # stay in (0,1]
        scored.append((sim,c)) #ppends similarioty score and character 

    scored.sort(key=lambda x: x[0], reverse=True) #sorts by the first thing in tuple, from decending 

    results = []
    for sim, c in scored[:top_k]:#goes to scores takes top 3 
        results.append({
            "id": c["id"],
            "name": c["name"],
            "series": c["series"],
            "similarity": round(sim, 4),
            "vector": c["vector"],
            "image_url": c.get("image_url"),
        })

    return results


