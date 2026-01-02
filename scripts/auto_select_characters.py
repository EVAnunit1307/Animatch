
import json
from pathlib import Path

# Map series name -> MAL anime id (must match your downloaded files)
SERIES_TO_ID = {
    "Naruto": 20,
    "One Piece": 21,
    "Jujutsu Kaisen": 40748,
}

MIN_FAVS = 5000
MAX_PER_SERIES = 12

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
            name = ch.get("name", "")
            cid = f"{series.lower().replace(' ', '_')}_{idx}"
            results.append(
                {
                    "id": cid,
                    "name": name,
                    "series": series,
                    "tags": ["anime"],
                    "image_url": img or "",
                }
            )

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} characters to {OUT}")


if __name__ == "__main__":
    main()
