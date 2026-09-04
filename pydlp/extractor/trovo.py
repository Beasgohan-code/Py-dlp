"""Trovo.live gaming live streams extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class TrovoIE(InfoExtractor):
    IE_NAME = "trovo"
    IE_DESC = "Trovo.live live streams and VODs extractor"
    _VALID_URL = r"https?://(?:www\.)?trovo\.live/(?:s/)?(?P<id>[a-zA-Z0-9_-]+)(?:\?vid=(?P<vid>[a-zA-Z0-9_-]+))?"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        channel_id = m.group("id") if m else "channel"
        vid = (m.group("vid") if m and "vid" in m.groupdict() else None) or channel_id

        webpage = self._download_webpage(url, video_id=vid)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Trovo Stream {channel_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m_hls in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m_hls.group(1), video_id=vid, fatal=False))

        return MediaInfo(
            id=vid,
            title=title,
            webpage_url=url,
            uploader=channel_id,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
