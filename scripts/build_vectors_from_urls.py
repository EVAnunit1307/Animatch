
import argparse
import json
import sys
import time
from pathlib import Path

import requests

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from animatch.app.services.landmarks import extract_landmarks, draw_landmarks_on_image
from animatch.app.services.features import landmarks_to_features


HANDPICKED_DEFAULT = Path("animatch/data/handpicked_characters.json")
OUT_DEFAULT = Path("animatch/app/data/anime_vectors.json")
SAVE_FAILED = True
FAILED_DIR = Path("animatch/data/failed_images")
REPORT = Path("animatch/data/vector_build_report.txt")
OVERLAY_DIR = Path("animatch/data/overlays")


def download_bytes(url: str) -> bytes:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.content

def fetch_char_detail_image(char_id: int) -> list[str]:
    """Try to get alternate image URLs from Jikan character detail."""
    urls = []
    try:
        resp = requests.get(f"https://api.jikan.moe/v4/characters/{char_id}", timeout=20)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        img = data.get("images", {}).get("jpg", {})
        for key in ("image_url", "large_image_url", "small_image_url"):
            u = img.get(key)
            if u:
                urls.append(u)
    except Exception:
        pass
    return urls


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--handpicked",
        default=str(HANDPICKED_DEFAULT),
        help="Path to handpicked JSON (default: animatch/data/handpicked_characters.json)",
    )
    parser.add_argument(
        "--out",
        default=str(OUT_DEFAULT),
        help="Output path for vectors (default: animatch/app/data/anime_vectors.json)",
    )
    args = parser.parse_args()

    handpicked_path = Path(args.handpicked)
    out_path = Path(args.out)
    items = json.loads(handpicked_path.read_text(encoding="utf-8"))
    results = []
    failed = 0
    noface = []
    errors = []

    if SAVE_FAILED:
        FAILED_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    for c in items:
        urls_to_try = []
        if c.get("image_url"):
            urls_to_try.append(c["image_url"])
        if c.get("image_small"):
            urls_to_try.append(c["image_small"])
        if c.get("char_id"):
            urls_to_try.extend(fetch_char_detail_image(c["char_id"]))
        # de-dupe while preserving order
        seen = set()
        urls_to_try = [u for u in urls_to_try if not (u in seen or seen.add(u))]

        tried = False
        success = False

        for url in urls_to_try:
            if not url:
                continue
            tried = True
            try:
                img_bytes = download_bytes(url)
                landmarks, quality = extract_landmarks(img_bytes)
                if landmarks is None:
                    continue

                vector = landmarks_to_features(landmarks)
                overlay_url = None
                try:
                    overlay_bytes = draw_landmarks_on_image(img_bytes, landmarks, radius=2)
                    overlay_path = OVERLAY_DIR / f"{c['id']}.png"
                    overlay_path.write_bytes(overlay_bytes)
                    overlay_url = f"/static/overlays/{overlay_path.name}"
                except Exception:
                    overlay_url = None

                record = {
                    "id": c["id"],
                    "name": c.get("name"),
                    "series": c.get("series"),
                    "tags": c.get("tags", []),
                    "vector": vector,
                    "image_url": url,
                    "overlay_url": overlay_url,
                }
                results.append(record)
                print("OK:", c["id"])
                success = True
                break
            except Exception as exc:
                # try next URL
                continue
            finally:
                time.sleep(0.05)  # be polite but faster

        if not success:
            failed += 1
            if not tried:
                print("Skip (no url):", c["id"])
                errors.append((c["id"], "no url"))
            else:
                print("No face or failed:", c["id"])
                noface.append(c["id"])
                if SAVE_FAILED and urls_to_try:
                    try:
                        (FAILED_DIR / f"{c['id']}_last.jpg").write_bytes(img_bytes)
                    except Exception:
                        pass

    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    report_lines = [
        f"Total entries: {len(items)}",
        f"Successful: {len(results)}",
        f"Failed: {failed}",
        f"No face: {', '.join(noface) if noface else '-'}",
        "Errors:",
    ]
    if errors:
        report_lines += [f"  {cid}: {msg}" for cid, msg in errors]
    else:
        report_lines.append("  -")

    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Done. Wrote {len(results)} entries to {out_path}. Failed: {failed}. See report: {REPORT}")


if __name__ == "__main__":
    main()
