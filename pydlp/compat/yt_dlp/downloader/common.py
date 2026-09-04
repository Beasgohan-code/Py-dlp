"""yt-dlp compatibility FileDownloader base shim."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydlp.core.progress import ProgressHook
from pydlp.downloader.base import BaseDownloader


class FileDownloader:
    """yt-dlp FileDownloader shim mapping to Py-dlp downloader engine."""

    def __init__(self, ydl: Any, params: Optional[Dict[str, Any]] = None):
        self.ydl = ydl
        self.params = params or {}

    def report_progress(self, status: Dict[str, Any]) -> None:
        pass

    def real_download(self, filename: str, info_dict: Dict[str, Any]) -> bool:
        raise NotImplementedError()
