"""Asynchronous wrapper for Py-dlp."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from pydlp.core.types import DownloadProgress, MediaInfo
from pydlp.pydlp import PyDLP


class AsyncPyDLP:
    """Asynchronous PyDLP engine designed for modern async frameworks."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self._pydlp = PyDLP(params)

    def add_progress_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        self._pydlp.add_progress_hook(hook)

    async def extract_info(
        self,
        url: str,
        download: bool = True,
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[MediaInfo]:
        """Runs media extraction and downloading asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._pydlp.extract_info, url, download, extra_info)

    async def download(self, url_list: Union[str, List[str]]) -> int:
        """Downloads a list of URLs asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._pydlp.download, url_list)
