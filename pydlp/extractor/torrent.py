"""Torrent and Magnet URI Stream Extractor for Py-dlp."""

from __future__ import annotations

import re
import urllib.parse
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class TorrentExtractor(InfoExtractor):
    """Extracts stream and metadata info from Magnet URIs and .torrent URLs."""

    _VALID_URL = r"^(?:magnet:\?xt=urn:btih:([a-zA-Z0-9]+)|https?://.+\.torrent(?:\?.+)?$)"
    IE_NAME = "torrent"
    IE_DESC = "BitTorrent & Magnet URI Media Resolver"

    def _match_url(self, url: str) -> bool:
        return url.startswith("magnet:?") or bool(re.match(self._VALID_URL, url, re.IGNORECASE))

    def _real_extract(self, url: str) -> MediaInfo:
        if url.startswith("magnet:?"):
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            xt = parsed.get("xt", [""])[0]
            dn = parsed.get("dn", ["BitTorrent Stream"])[0]
            trackers = parsed.get("tr", [])

            info_hash = xt.split(":")[-1] if ":" in xt else xt
            title = dn

            formats = [
                MediaFormat(
                    format_id="torrent-stream",
                    url=url,
                    ext="mp4",
                    format_note=f"P2P BitTorrent Stream (Hash: {info_hash[:8]})",
                    vcodec="auto",
                    acodec="auto",
                )
            ]

            return MediaInfo(
                id=info_hash or "torrent",
                title=title,
                extractor=self.IE_NAME,
                webpage_url=url,
                formats=formats,
                description=f"BitTorrent Magnet Resource with {len(trackers)} tracker(s).",
                tags=trackers,
            )

        # HTTP Torrent file link
        title = url.split("/")[-1].split("?")[0].replace(".torrent", "")
        return MediaInfo(
            id=title,
            title=title,
            extractor=self.IE_NAME,
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="torrent-file",
                    url=url,
                    ext="torrent",
                    format_note="BitTorrent Metadata File",
                )
            ],
            description=f"BitTorrent source: {url}",
        )
