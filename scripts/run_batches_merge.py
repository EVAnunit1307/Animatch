
import json
import subprocess
import sys
from pathlib import Path

BATCH_DIR = Path("animatch/data/batches")
MERGED_OUT = Path("animatch/app/data/anime_vectors.json")
BATCH_OUT_DIR = Path("animatch/data/batch_vectors")


def main():
    BATCH_OUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = []
    batch_files = sorted(BATCH_DIR.glob("*.json"))
    for bf in batch_files:
        out_path = BATCH_OUT_DIR / f"{bf.stem}_vectors.json"
        print(f"Building batch {bf.name} -> {out_path.name}")
        subprocess.check_call(
            [sys.executable, "scripts/build_vectors_from_urls.py", "--handpicked", str(bf), "--out", str(out_path)]
        )
        data = json.loads(out_path.read_text(encoding="utf-8"))
        combined.extend(data)

    MERGED_OUT.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Merged {len(combined)} vectors into {MERGED_OUT}")


if __name__ == "__main__":
    main()
