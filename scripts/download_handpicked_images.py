"""
Download images for handpicked characters listed in animatch/data/handpicked_characters.json.
"""
import json
import time
from pathlib import Path

import requests


def main() -> None:
    src = Path("animatch/data/handpicked_characters.json")
    items = json.loads(src.read_text(encoding="utf-8"))

    out_dir = Path("animatch/data/images")
    out_dir.mkdir(parents=True, exist_ok=True)

    for c in items:
        url = c.get("image_url")
        if not url:
            print("Skip (no url):", c["id"])
            continue

        out_path = out_dir / f'{c["id"]}.jpg'
        if out_path.exists():
            print("Exists:", out_path.name)
            continue

        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            print("Fail:", c["id"], r.status_code)
            continue

        out_path.write_bytes(r.content)
        print("Saved:", out_path.name)

        time.sleep(0.4)


if __name__ == "__main__":
    main()
