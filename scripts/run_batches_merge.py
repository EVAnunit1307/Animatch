
import argparse
import json
import subprocess
import sys
from pathlib import Path

BATCH_DIR_DEFAULT = Path("animatch/data/batches_auto")
MERGED_OUT_DEFAULT = Path("animatch/app/data/anime_vectors.json")
BATCH_OUT_DIR = Path("animatch/data/batch_vectors")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-dir", default=str(BATCH_DIR_DEFAULT), help="Directory of batch JSON files.")
    parser.add_argument("--out", default=str(MERGED_OUT_DEFAULT), help="Output path for merged vectors.")
    args = parser.parse_args()

    batch_dir = Path(args.batch_dir)
    if not batch_dir.exists():
        raise SystemExit(f"Batch dir not found: {batch_dir}")

    BATCH_OUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = []
    batch_files = sorted(batch_dir.glob("*.json"))
    for bf in batch_files:
        out_path = BATCH_OUT_DIR / f"{bf.stem}_vectors.json"
        print(f"Building batch {bf.name} -> {out_path.name}")
        subprocess.check_call(
            [sys.executable, "scripts/build_vectors_from_urls.py", "--handpicked", str(bf), "--out", str(out_path)]
        )
        data = json.loads(out_path.read_text(encoding="utf-8"))
        combined.extend(data)

    merged_out = Path(args.out)
    merged_out.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Merged {len(combined)} vectors into {merged_out}")


if __name__ == "__main__":
    main()
