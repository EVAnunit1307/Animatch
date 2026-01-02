
import json
import re
from pathlib import Path

REPORT = Path("animatch/data/vector_build_report.txt")
SRC = Path("animatch/data/handpicked_auto.json")
OUT = Path("animatch/data/handpicked_auto_clean.json")


def parse_no_face(report_path: Path) -> set[str]:
    ids = set()
    txt = report_path.read_text(encoding="utf-8")
    m = re.search(r"No face:\s*(.*)", txt)
    if not m:
        return ids
    raw = m.group(1)
    for part in raw.split(","):
        pid = part.strip()
        if pid and pid != "-":
            ids.add(pid)
    return ids


def main() -> None:
    if not REPORT.exists() or not SRC.exists():
        print("Report or source file missing; nothing to prune.")
        return

    no_face_ids = parse_no_face(REPORT)
    data = json.loads(SRC.read_text(encoding="utf-8"))
    kept = [c for c in data if c.get("id") not in no_face_ids]
    OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Pruned {len(data)-len(kept)} entries (no face). Wrote {len(kept)} to {OUT}")


if __name__ == "__main__":
    main()
