"""AfreecaTV and SOOP Live Korean streaming extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class AfreecaTVIE(InfoExtractor):
    IE_NAME = "afreecatv"
    IE_DESC = "AfreecaTV & SOOP Live Korean streams extractor"
    _VALID_URL = r"https?://(?:www\.|play\.)?(?:afreecatv\.com|sooplive\.co\.kr)/(?:player/)?(?P<id>[a-zA-Z0-9_-]+)(?:/(?P<bno>\d+))?"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        stream_id = m.group("bno") or m.group("id") or "stream"
        webpage = self._download_webpage(url, video_id=stream_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"AfreecaTV {stream_id}")
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
