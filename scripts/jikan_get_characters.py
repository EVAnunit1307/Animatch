
import json
import sys
import time
from pathlib import Path

import requests


def fetch_characters(anime_id: int) -> list:
    url = f"https://api.jikan.moe/v4/anime/{anime_id}/characters"
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    return res.json().get("data", [])


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/jikan_get_characters.py <mal_anime_id>")
        raise SystemExit(1)

    anime_id = int(sys.argv[1])
    data = fetch_characters(anime_id)

    out_dir = Path("animatch/data/jikan")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{anime_id}_characters.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(data)} characters to {out_path}")
    # Be polite to the API if running in a loop
    time.sleep(0.35)


if __name__ == "__main__":
    main()
