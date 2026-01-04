"""
Fetch character lists for all series in auto_select_characters.SERIES_TO_ID.
"""
from pathlib import Path
import importlib
import subprocess
import sys
from pathlib import Path

# ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    auto_mod = importlib.import_module("scripts.auto_select_characters")
    if hasattr(auto_mod, "load_series_to_id"):
        series_to_id = auto_mod.load_series_to_id()
    else:
        series_to_id = getattr(auto_mod, "SERIES_TO_ID", {})
    for series, aid in series_to_id.items():
        print(f"Fetching {series} ({aid})")
        subprocess.check_call([sys.executable, "scripts/jikan_get_characters.py", str(aid)])


if __name__ == "__main__":
    main()
