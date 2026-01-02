

import json
import re
from pathlib import Path


# Map series -> anime MAL id (for the character list file)
SERIES_TO_ID = {
    "Naruto": 20,
    "One Piece": 21,
    "Jujutsu Kaisen": 40748,
}

DATA_DIR = Path("animatch/data")
HANDPICKED_PATH = DATA_DIR / "handpicked_characters.json"
JIKAN_DIR = DATA_DIR / "jikan"


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def name_variants(name: str) -> set[str]:
    """Return normalized variants (handles 'Last, First')."""
    variants = {normalize(name)}
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            rev = f"{parts[1]} {parts[0]}"
            variants.add(normalize(rev))
    return variants


def load_character_map(anime_id: int) -> dict[str, str]:
    """Map normalized character names to their jpg image_url."""
    path = JIKAN_DIR / f"{anime_id}_characters.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping = {}
    for entry in data:
        name = entry.get("character", {}).get("name", "")
        img = entry.get("character", {}).get("images", {}).get("jpg", {}).get("image_url")
        if not name or not img:
            continue
        for v in name_variants(name):
            mapping[v] = img
    return mapping


def main() -> None:
    items = json.loads(HANDPICKED_PATH.read_text(encoding="utf-8"))

    # Build per-series character maps
    series_maps: dict[str, dict[str, str]] = {}
    for series, aid in SERIES_TO_ID.items():
        series_maps[series] = load_character_map(aid)

    filled = 0
    for c in items:
        if c.get("image_url"):
            continue
        series = c.get("series")
        if series not in series_maps:
            continue
        cmap = series_maps[series]
        n = normalize(c.get("name", ""))
        url = cmap.get(n)
        if not url:
            # try loose: any variant that matches substring
            for k, v in cmap.items():
                if n in k or k in n:
                    url = v
                    break
        if url:
            c["image_url"] = url
            filled += 1

    HANDPICKED_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Filled image_url for {filled} entries")


if __name__ == "__main__":
    main()
