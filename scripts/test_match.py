from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from animatch.app.services.match import load_characters

chars = load_characters()
print("Loaded characters:", len(chars))
print("First one:", chars[0]["name"])
