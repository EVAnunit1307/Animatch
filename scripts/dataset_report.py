import json
from collections import Counter
from pathlib import Path


def main():
    path = Path("animatch/app/data/anime_vectors.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    total = len(data)
    missing_overlay = [d["id"] for d in data if not d.get("overlay_url")]
    series_counts = Counter(d.get("series", "Unknown") for d in data)

    print(f"Total entries: {total}")
    print(f"Missing overlays: {len(missing_overlay)}")
    if missing_overlay:
        print("Examples without overlay:", ", ".join(missing_overlay[:10]))

    print("\nBy series (top 20):")
    for series, cnt in series_counts.most_common(20):
        print(f"- {series}: {cnt}")


if __name__ == "__main__":
    main()
