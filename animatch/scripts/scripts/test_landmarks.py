
from pathlib import Path
import subprocess
import sys

new_script = Path(__file__).resolve().parents[2] / "scripts" / "test_landmarks.py"
if not new_script.exists():
    print(f"Updated script not found: {new_script}", file=sys.stderr)
    sys.exit(1)

# Execute the new script using the current Python executable and forward args
sys.exit(subprocess.call([sys.executable, str(new_script)] + sys.argv[1:]))
