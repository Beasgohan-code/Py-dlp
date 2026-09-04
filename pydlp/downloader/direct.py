"""Direct downloader router that selects the optimal download engine."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydlp.core.http import HttpClient
from pydlp.core.plugins import get_custom_downloaders
from pydlp.core.types import MediaFormat
from pydlp.downloader.base import BaseDownloader
from pydlp.downloader.dash import DashDownloader
from pydlp.downloader.external import ExternalDownloader
from pydlp.downloader.hls import HlsDownloader
from pydlp.downloader.hls_live import HLSLiveDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.multisegment import MultiSegmentDownloader
from pydlp.downloader.resumable import ResumableDownloader
from pydlp.downloader.turbo import TurboDownloader
from pydlp.downloader.websocket import WebSocketDownloader

# Backward compatibility alias
DirectDownloader = HttpDownloader


def get_downloader(
    fmt: MediaFormat,
    http_client: HttpClient,
    options: Optional[Dict[str, Any]] = None,
) -> BaseDownloader:
    """Returns the optimal downloader for the given format."""
    opts = options or {}
    proto = (fmt.protocol or "").lower()
    url = (fmt.url or "").lower()

    # Check custom plugin downloaders
    custom_dls = get_custom_downloaders()
    if proto in custom_dls:
        return custom_dls[proto](http_client, opts)

    # External CLI downloaders (aria2c, curl, wget, axel, ffmpeg)
    if opts.get("external_downloader"):
        return ExternalDownloader(http_client, opts)

    if fmt.is_hls or "m3u8" in proto or ".m3u8" in url:
        if opts.get("live_record_duration"):
            return HLSLiveDownloader(http_client, opts)
        return HlsDownloader(http_client, opts)
    elif fmt.is_dash or "mpd" in proto or ".mpd" in url:
        return DashDownloader(http_client, opts)
    elif opts.get("turbo", False):
        return TurboDownloader(http_client, opts)
    elif int(opts.get("concurrent_fragments", 1)) > 1:
        return MultiSegmentDownloader(http_client, opts)
    elif opts.get("continue_dl", True):
        return ResumableDownloader(http_client, opts)
    else:
        return HttpDownloader(http_client, opts)
