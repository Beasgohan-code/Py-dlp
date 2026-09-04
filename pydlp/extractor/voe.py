"""Voe.sx video extractor."""

from __future__ import annotations

import base64
import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class VoeIE(InfoExtractor):
    """Extractor for Voe.sx videos."""

    IE_NAME = "voe"
    IE_DESC = "Voe.sx and mirror video hosts"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:voe\.sx|repacklab\.(?:com|org)|steamyplay\.(?:com|org))/(?:e/)?(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        embed_url = f"https://voe.sx/e/{video_id}"
        webpage = self._download_webpage(embed_url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Voe Video {video_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Look for sources: {'hls': '...', 'mp4': '...'} or base64 encoded hls
            hls_match = re.search(r'["\']hls["\']\s*:\s*["\']([^"\']+)["\']', webpage)
            if hls_match:
                hls_raw = hls_match.group(1)
                # Check if base64 encoded
                if not hls_raw.startswith("http"):
                    try:
                        hls_raw = base64.b64decode(hls_raw).decode("utf-8")
                    except Exception:
                        pass
                if ".m3u8" in hls_raw:
                    formats.extend(self._extract_m3u8_formats(hls_raw, video_id))

            # Look for direct mp4
            mp4_match = re.search(r'["\']mp4["\']\s*:\s*["\']([^"\']+)["\']', webpage)
            if mp4_match:
                mp4_raw = mp4_match.group(1)
                if not mp4_raw.startswith("http"):
                    try:
                        mp4_raw = base64.b64decode(mp4_raw).decode("utf-8")
                    except Exception:
                        pass
                formats.append(MediaFormat(format_id="voe-mp4", url=mp4_raw, ext="mp4"))

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=embed_url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=embed_url,
            thumbnail=thumbnail,
            formats=formats,
        )
