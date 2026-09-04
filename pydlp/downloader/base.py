"""Base downloader interface for Py-dlp."""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.progress import ProgressHookDispatcher, SpeedCalculator
from pydlp.core.ratelimit import RateLimiter, parse_rate_limit
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo


class BaseDownloader(ABC):
    """Abstract base class for all download engines."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        self.http = http_client
        self.options = options or {}
        self.progress_dispatcher = ProgressHookDispatcher()
        self.speed_calc = SpeedCalculator()
        self._cancel_requested = False
        rate_limit_val = parse_rate_limit(self.options.get("limit_rate") or self.options.get("ratelimit"))
        self.rate_limiter = RateLimiter(rate_limit_val)

    def throttle(self, bytes_transferred: int) -> None:
        """Throttle transfer speed if rate limiting is enabled."""
        if self.rate_limiter:
            self.rate_limiter.throttle(bytes_transferred)

    def add_progress_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        self.progress_dispatcher.add_hook(hook)

    def cancel(self) -> None:
        self._cancel_requested = True

    def check_canceled(self) -> None:
        if self._cancel_requested:
            raise CancelRequested("Download was cancelled by user")

    def _get_target_paths(self, filename: str) -> tuple[str, str]:
        """Returns (final_path, part_path)."""
        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        if self.options.get("nopart", False):
            return filename, filename

        part_filename = f"{filename}.part"
        return filename, part_filename

    @abstractmethod
    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        """Downloads the format into filename. Returns True on success."""
        pass
