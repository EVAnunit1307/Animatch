from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from animatch.app.services.match import load_characters

chars = load_characters()
print("Loaded characters:", len(chars))
print("First one:", chars[0]["name"])

from animatch.app.services.match import load_characters, distance

user = {
    "face_ratio": 0.62,
    "eye_spacing": 0.44,
    "eye_openness": 0.52,
    "jaw_angle": 0.33,
    "chin_ratio": 0.41,
    "brow_height": 0.47
}

chars = load_characters()

d = distance(user, chars[0]["vector"])
print("Distance to first character:", d)

from animatch.app.services.match import load_characters, distance

user = {
    "face_ratio": 0.62,
    "eye_spacing": 0.44,
    "eye_openness": 0.52,
    "jaw_angle": 0.33,
    "chin_ratio": 0.41,
    "brow_height": 0.47
}

chars = load_characters()

best = None
best_score = None

for c in chars:
    d = distance(user, c["vector"])
    print(c["name"], "score:", round(d, 4))

    if best_score is None or d < best_score:
        best_score = d
        best = c

print("Best match:", best["name"], "with score", round(best_score, 4))
