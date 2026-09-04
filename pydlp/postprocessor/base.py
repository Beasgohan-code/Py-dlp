"""Base post-processor interface for Py-dlp."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.types import MediaInfo


class BasePostProcessor(ABC):
    """Abstract base class for all post-processors."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}

    @abstractmethod
    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        """Runs post-processing on media info. Returns (files_to_delete, updated_info)."""
        pass
