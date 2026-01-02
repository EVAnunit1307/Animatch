
import json
import sys
import time
from pathlib import Path

import requests

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from animatch.app.services.landmarks import extract_landmarks
from animatch.app.services.features import landmarks_to_features


HANDPICKED = Path("animatch/data/handpicked_characters.json")
OUT = Path("animatch/app/data/anime_vectors.json")
SAVE_FAILED = True
FAILED_DIR = Path("animatch/data/failed_images")
REPORT = Path("animatch/data/vector_build_report.txt")


def download_bytes(url: str) -> bytes:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.content


def main() -> None:
    items = json.loads(HANDPICKED.read_text(encoding="utf-8"))
    results = []
    failed = 0
    noface = []
    errors = []

    if SAVE_FAILED:
        FAILED_DIR.mkdir(parents=True, exist_ok=True)

    for c in items:
        url = c.get("image_url")
        if not url:
            print("Skip (no url):", c["id"])
            continue

        try:
            img_bytes = download_bytes(url)
            landmarks, quality = extract_landmarks(img_bytes)
            if landmarks is None:
                print("No face:", c["id"])
                failed += 1
                noface.append(c["id"])
                if SAVE_FAILED:
                    (FAILED_DIR / f"{c['id']}_noface.jpg").write_bytes(img_bytes)
                continue

            vector = landmarks_to_features(landmarks)
            record = {
                "id": c["id"],
                "name": c.get("name"),
                "series": c.get("series"),
                "tags": c.get("tags", []),
                "vector": vector,
                "image_url": url,
            }
            results.append(record)
            print("OK:", c["id"])

        except Exception as exc:
            print("Fail:", c["id"], exc)
            failed += 1
            errors.append((c["id"], str(exc)))
            if SAVE_FAILED:
                (FAILED_DIR / f"{c['id']}_error.txt").write_text(str(exc), encoding="utf-8")
            continue
        finally:
            time.sleep(0.3)  # be polite

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
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

    print(f"Done. Wrote {len(results)} entries to {OUT}. Failed: {failed}. See report: {REPORT}")


if __name__ == "__main__":
    main()
