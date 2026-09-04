"""Tube8 media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class Tube8IE(InfoExtractor):
    IE_NAME = "tube8"
    IE_DESC = "Tube8 video extractor"
    _VALID_URL = r"https?://(?:www\.)?tube8\.com/(?:[^/]+/)*(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Tube8 Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
