"""Explainability helpers for matches."""
from typing import Dict


def summarize(match_details: Dict) -> str:
    return f"Explained: {match_details.get('method', 'unknown')}"
