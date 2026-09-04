"""Nebula and Floatplane video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class NebulaIE(InfoExtractor):
    """Extractor for Nebula.tv and Floatplane.com videos."""

    IE_NAME = "nebula"
    IE_DESC = "Nebula.tv and Floatplane.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:nebula\.tv/videos/|floatplane\.com/post/)(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"Nebula Video {video_id}"
        description = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            og_desc = self._html_search_meta(["og:description"], webpage)
            dur_str = self._html_search_meta(["video:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if og_desc:
                description = clean_html(og_desc)
            if dur_str:
                duration = parse_duration(dur_str)

            # Look for HLS manifests in JSON state
            m3u8_matches = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            for m_url in m3u8_matches:
                formats.extend(self._extract_m3u8_formats(m_url, video_id))

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
