import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--handpicked",
        default="animatch/data/handpicked_characters.json",
        help="Path to handpicked JSON file.",
    )
    parser.add_argument(
        "--out-dir",
        default="animatch/data/batches_auto",
        help="Output directory for batch JSON files.",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=60,
        help="Batch size.",
    )
    args = parser.parse_args()

    items = json.loads(Path(args.handpicked).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(items)
    batch_size = max(1, args.size)
    count = 0

    for idx in range(0, total, batch_size):
        batch = items[idx : idx + batch_size]
        out_path = out_dir / f"batch_{(idx // batch_size) + 1:03d}.json"
        out_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1

    print(f"Wrote {count} batches to {out_dir} from {total} items.")


if __name__ == "__main__":
    main()
