"""Simple dataclasses for core domain objects (no extra deps)."""
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Landmark:
    id: str
    name: str
    metadata: Dict[str, Any]


@dataclass
class Feature:
    id: str
    vector: List[float]


@dataclass
class MatchResult:
    a_id: str
    b_id: str
    score: float
    details: Dict[str, Any]
