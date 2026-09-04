"""Chaturbate and Stripchat live stream extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class ChaturbateIE(InfoExtractor):
    """Extractor for Chaturbate and Stripchat live cam streams."""

    IE_NAME = "chaturbate"
    IE_DESC = "Chaturbate.com and Stripchat.com live streams"
    _VALID_URL = r"^(?:https?://)?(?:www\.|[a-z]{2}\.)?(?:chaturbate\.com/(?P<id>[a-zA-Z0-9_-]+)|stripchat\.com/(?P<sc_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        room_id = m.group("id") or m.group("sc_id")
        webpage = self._download_webpage(url, video_id=room_id, fatal=False)

        title = f"Live Cam {room_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Find m3u8 stream link in initial-room-data or hls_source
            hls_matches = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            for hls_url in hls_matches:
                if "playlist" in hls_url or "live" in hls_url or "stream" in hls_url or "chunklist" in hls_url:
                    formats.extend(self._extract_m3u8_formats(hls_url, room_id, note="Live Stream"))

        if not formats:
            formats.append(
                MediaFormat(
                    format_id="hls-live",
                    url=url,
                    ext="mp4",
                    protocol="m3u8_native",
                )
            )

        return MediaInfo(
            id=room_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            is_live=True,
            age_limit=18,
            formats=formats,
        )
