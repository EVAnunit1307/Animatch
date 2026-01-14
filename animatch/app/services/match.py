import json
import math 
from pathlib import Path
from typing import Tuple, List

_CHAR_CACHE: Tuple[List[dict], dict, float] | None = None


def load_characters():
    """Load characters once and cache with precomputed stats.
    Auto-refreshes if the vectors file changes (mtime)."""
    global _CHAR_CACHE
    data_path = Path(__file__).resolve().parents[1] / "data" / "anime_vectors.json" #fetchs and appends anime vectors 
    mtime = data_path.stat().st_mtime

    if _CHAR_CACHE is not None:
        cached_chars, cached_stats, cached_mtime = _CHAR_CACHE
        if cached_mtime == mtime:
            return _CHAR_CACHE

    with open(data_path, "r", encoding="utf-8") as file:
        chars = json.load(file)
    stats = compute_stats(chars)
    _CHAR_CACHE = (chars, stats, mtime)
    return _CHAR_CACHE

features = [
    "face_ratio",
    "eye_spacing",
    "eye_openness",
    "jaw_angle",
    "chin_ratio",
    "brow_height",
    "mouth_width",
    "nose_length",
]

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


def center_distance(vec):
    """Distance from the dataset mean in z-score space."""
    total = 0.0
    for f in features:
        total += vec[f] * vec[f]
    return math.sqrt(total)


def select_diverse(scored, top_k, min_dist=0.55):
    """Pick results with series and geometry diversity."""
    selected = []
    used_series = set()

    for item in scored:
        if len(selected) >= top_k:
            break
        series = item["char"].get("series")
        if series in used_series:
            continue
        too_close = False
        for s in selected:
            if distance(item["norm"], s["norm"]) < min_dist:
                too_close = True
                break
        if too_close:
            continue
        selected.append(item)
        used_series.add(series)

    if len(selected) < top_k:
        for item in scored:
            if len(selected) >= top_k:
                break
            too_close = False
            for s in selected:
                if distance(item["norm"], s["norm"]) < (min_dist * 0.6):
                    too_close = True
                    break
            if too_close:
                continue
            selected.append(item)

    return selected


def match_characters (user_features, top_k=4): #default top 4 
    chars, stats, _ = load_characters()
    user_norm = normalize(user_features, stats)
    scored = []

    for c in chars:
        c_norm = normalize(c["vector"], stats)
        d = distance(user_norm, c_norm)
        sim = 1.0 / (1.0 + d)  # stay in (0,1]
        # boost more distinctive faces so the "average" vector doesn't dominate
        distinct = center_distance(c_norm)
        boost = 1.0 + min(distinct / 3.0, 0.4)
        sim_adj = sim * boost
        scored.append({"sim": sim_adj, "raw": sim, "char": c, "norm": c_norm})

    scored.sort(key=lambda x: x["sim"], reverse=True) #sorts by the first thing in tuple, from decending 

    results = []
    final = select_diverse(scored, top_k)
    for item in final:#goes to scores takes top 3 
        sim = item["raw"]
        c = item["char"]
        # Mild boost for friendly UX (cap at 100)
        pct = max(0.0, min(100.0, sim * 100.0 * 1.75))
        if pct >= 50:
            badge = "Good"
        elif pct >= 30:
            badge = "OK"
        else:
            badge = "Weak"
        results.append({
            "id": c["id"],
            "name": c["name"],
            "series": c["series"],
            "similarity": round(sim, 4),
            "similarity_pct": round(pct, 1),
            "badge": badge,
            "vector": c["vector"],
            "image_url": c.get("image_url"),
            "overlay_url": c.get("overlay_url"),
        })

    return results


