"""Matching logic between two feature sets."""
from typing import Tuple


def match(a: list, b: list) -> Tuple[float, dict]:
    """Return a score and details (placeholder uses simple dot product normed)."""
    if not a or not b:
        return 0.0, {}
    # naive similarity
    score = sum(x * y for x, y in zip(a, b)) / max(1.0, len(a))
    return float(score), {"method": "naive"}
