import json
import time
from pathlib import Path

import requests

API_URL = "https://api.jikan.moe/v4/anime"
VECTORS_PATH = Path("animatch/app/data/anime_vectors.json")
TITLES_PATH = Path("animatch/app/data/anime_titles.txt")
OUT_PATH = Path("animatch/app/data/series_posters.json")


def load_series() -> list[str]:
    if TITLES_PATH.exists():
        titles = [line.strip() for line in TITLES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        return sorted(set(titles))
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    return sorted({c.get("series") for c in data if c.get("series")})


def fetch_poster(title: str) -> dict:
    resp = requests.get(API_URL, params={"q": title, "limit": 1}, timeout=20)
    resp.raise_for_status()
    items = resp.json().get("data", [])
    if not items:
        return {"series": title, "image_url": "", "url": ""}
    item = items[0]
    imgs = item.get("images", {}).get("jpg", {})
    image_url = imgs.get("large_image_url") or imgs.get("image_url") or ""
    url = item.get("url") or ""
    return {"series": title, "image_url": image_url, "url": url}


def main() -> None:
    series = load_series()
    results = []
    for title in series:
        try:
            results.append(fetch_poster(title))
        except Exception as exc:
            results.append({"series": title, "image_url": "", "url": ""})
            print(f"Warn: {title} -> {exc}")
        time.sleep(0.4)
    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} series to {OUT_PATH}")


if __name__ == "__main__":
    main()
