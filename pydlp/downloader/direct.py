"""Direct downloader router that selects the best download engine."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydlp.core.http import HttpClient
from pydlp.core.types import MediaFormat
from pydlp.downloader.base import BaseDownloader
from pydlp.downloader.dash import DashDownloader
from pydlp.downloader.hls import HlsDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.multisegment import MultiSegmentDownloader


def get_downloader(
    fmt: MediaFormat,
    http_client: HttpClient,
    options: Optional[Dict[str, Any]] = None,
) -> BaseDownloader:
    """Returns the optimal downloader for the given format."""
    opts = options or {}
    proto = (fmt.protocol or "").lower()
    url = (fmt.url or "").lower()

    if fmt.is_hls or "m3u8" in proto or ".m3u8" in url:
        return HlsDownloader(http_client, opts)
    elif fmt.is_dash or "mpd" in proto or ".mpd" in url:
        return DashDownloader(http_client, opts)
    elif opts.get("concurrent_fragments", 1) > 1:
        return MultiSegmentDownloader(http_client, opts)
    else:
        return HttpDownloader(http_client, opts)
