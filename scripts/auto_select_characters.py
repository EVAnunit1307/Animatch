
import json
from pathlib import Path

# Map series name -> MAL anime id (must match your downloaded files)
SERIES_TO_ID = {
    "Naruto": 20,
    "One Piece": 21,
    "Jujutsu Kaisen": 40748,
    "Demon Slayer": 38000,
    "Attack on Titan": 16498,
    "My Hero Academia": 31964,
    "Fullmetal Alchemist: Brotherhood": 5114,
    "Bleach": 269,
    "One Punch Man": 30276,
    "Death Note": 1535,
    "Dragon Ball Z": 813,
    "Hunter x Hunter": 11061,
    "Chainsaw Man": 44511,
    "Spy x Family": 50265,
    "JoJo's Bizarre Adventure": 14719,
    "Haikyuu!!": 20583,
    "Kuroko's Basketball": 11771,
    "Slam Dunk": 170,
    "Re:Zero": 31240,
    "Sword Art Online": 11757,
    "No Game No Life": 19815,
    "Shield Hero": 35790,
    "Slime": 37430,
    "Tokyo Ghoul": 22319,
    "Fairy Tail": 6702,
    "Black Clover": 34572,
    "Dr. Stone": 38691,
    "Blue Lock": 49596,
    "Vinland Saga": 37521,
    "Code Geass": 1575,
    "Neon Genesis Evangelion": 30,
}

# Adjust these if you want more/fewer per series
# Lowered favorites threshold to widen pool; bumped cap for bigger series.
MIN_FAVS = 1500
MAX_PER_SERIES = 30

DATA_DIR = Path("animatch/data")
JIKAN_DIR = DATA_DIR / "jikan"
OUT = DATA_DIR / "handpicked_auto.json"


def load_characters(anime_id: int):
    path = JIKAN_DIR / f"{anime_id}_characters.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def pick_top(chars, max_n):
    picked = []
    for c in chars:
        role = c.get("role", "")
        favs = c.get("favorites", 0) or 0
        if role == "Main" or favs >= MIN_FAVS:
            picked.append(c)
        if len(picked) >= max_n:
            break
    return picked


def main():
    results = []
    for series, aid in SERIES_TO_ID.items():
        data = load_characters(aid)
        # sort by favorites desc
        data.sort(key=lambda x: x.get("favorites", 0) or 0, reverse=True)
        top_chars = pick_top(data, MAX_PER_SERIES)
        for idx, c in enumerate(top_chars):
            ch = c.get("character", {})
            img = ch.get("images", {}).get("jpg", {}).get("image_url")
            img_small = ch.get("images", {}).get("jpg", {}).get("small_image_url")
            img_large = ch.get("images", {}).get("jpg", {}).get("large_image_url")
            char_id = ch.get("mal_id")
            name = ch.get("name", "")
            cid = f"{series.lower().replace(' ', '_')}_{idx}"
            results.append(
                {
                    "id": cid,
                    "name": name,
                    "series": series,
                    "tags": ["anime"],
                    "image_url": img or "",
                    "image_small": img_small or "",
                    "image_large": img_large or "",
                    "char_id": char_id,
                }
            )

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} characters to {OUT}")


if __name__ == "__main__":
    main()
