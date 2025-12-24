"""Landmark loading utilities."""
import json
from pathlib import Path
from typing import Iterable


def load_landmarks(path: str | Path) -> Iterable[dict]:
    """Load landmark records from a JSON file (one array of objects expected)."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("landmark data must be a list")
        return data
