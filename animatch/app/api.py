"""Small, framework-agnostic helper API for Animatch (placeholders)."""
from typing import List

# import top-level package metadata
from .. import __version__


class AnimatchAPI:
    """Minimal API class to expose services."""

    def __init__(self) -> None:
        self._services = ["landmarks", "features", "match", "explain"]

    def list_services(self) -> List[str]:
        return list(self._services)

    # placeholder for more functionality
    def ping(self) -> str:
        return f"Animatch API v{__version__} is alive"
