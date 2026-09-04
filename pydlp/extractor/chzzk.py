"""Naver Chzzk Korean streaming extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class ChzzkIE(InfoExtractor):
    IE_NAME = "chzzk"
    IE_DESC = "Naver Chzzk live streaming and video extractor"
    _VALID_URL = r"https?://(?:www\.)?chzzk\.naver\.com/(?:live/|video/)?(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        stream_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=stream_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Chzzk Stream {stream_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m_hls in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m_hls.group(1), video_id=stream_id, fatal=False))

        return MediaInfo(
            id=stream_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
