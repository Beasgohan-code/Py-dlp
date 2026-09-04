"""Universal All-Rounder Downloader dispatch engine for Py-dlp."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

from pydlp.core.exceptions import DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
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


class AllRounderDownloader(BaseDownloader):
    """The All-Rounder Downloader: dynamically inspects media protocols, streams, and options

    to dispatch the optimal high-performance downloading engine with seamless fallbacks.
    """

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(http_client, options)
        self._active_downloader: Optional[BaseDownloader] = None

    def _select_downloader(self, fmt: MediaFormat, info_dict: MediaInfo) -> BaseDownloader:
        protocol = (fmt.protocol or "").lower()
        url = fmt.url or ""

        # 1. Check if external downloader is explicitly requested
        if self.options.get("external_downloader"):
            return ExternalDownloader(self.http, self.options)

        # 2. Check live streaming
        if info_dict.is_live or self.options.get("live_record_duration"):
            if protocol in ("m3u8", "m3u8_native", "hls") or ".m3u8" in url:
                return HLSLiveDownloader(self.http, self.options)
            elif url.startswith(("ws://", "wss://", "http://", "https://")):
                return WebSocketDownloader(self.http, self.options)

        # 3. HLS Master / Segmented streams
        if protocol in ("m3u8", "m3u8_native", "hls") or ".m3u8" in url:
            return HlsDownloader(self.http, self.options)

        # 4. MPEG-DASH manifests
        if protocol in ("dash", "mpd") or ".mpd" in url:
            return DashDownloader(self.http, self.options)

        # 5. Turbo multi-connection engine (if enabled)
        if self.options.get("turbo", False):
            return TurboDownloader(self.http, self.options)

        # 6. Multi-segment chunk downloader (if concurrent_fragments > 1)
        if int(self.options.get("concurrent_fragments", 1)) > 1:
            return MultiSegmentDownloader(self.http, self.options)

        # 7. Resumable stateful downloader (if continue_dl enabled with state tracking)
        if self.options.get("continue_dl", True):
            return ResumableDownloader(self.http, self.options)

        # 8. Standard HTTP Downloader
        return HttpDownloader(self.http, self.options)

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        downloader = self._select_downloader(fmt, info_dict)
        self._active_downloader = downloader

        # Propagate hooks
        for hook in self.progress_dispatcher._hooks:
            downloader.add_progress_hook(hook)

        try:
            return downloader.download(filename, info_dict, fmt)
        except Exception as e:
            # Automatic resilient fallback to standard HTTP / Resumable downloader
            if not isinstance(downloader, (HttpDownloader, ResumableDownloader)):
                fallback = ResumableDownloader(self.http, self.options)
                for hook in self.progress_dispatcher._hooks:
                    fallback.add_progress_hook(hook)
                return fallback.download(filename, info_dict, fmt)
            raise
