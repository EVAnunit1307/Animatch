"""Feature extraction utilities (placeholder implementations)."""
from typing import List


def extract_features(blob: bytes) -> List[float]:
    """Placeholder function: replace with real model-based extraction."""
    # return a fixed-length dummy vector for now
    return [float(b % 256) for b in blob[:128]]
