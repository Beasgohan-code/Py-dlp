"""CamSoda, Cam4, and LiveJasmin live stream extractors."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class CamSodaIE(InfoExtractor):
    IE_NAME = "camsoda"
    IE_DESC = "CamSoda, Cam4, and LiveJasmin cam extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:camsoda\.com/(?P<id>[a-zA-Z0-9_-]+)|cam4\.com/(?P<cam4_id>[a-zA-Z0-9_-]+)|livejasmin\.com/(?:[a-z]{2}/)?models/(?P<jasmin_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        model_name = m.group("id") or m.group("cam4_id") or m.group("jasmin_id") or "model"
        webpage = self._download_webpage(url, video_id=model_name)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Live Cam {model_name}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find HLS stream links
        for m_hls in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m_hls.group(1), video_id=model_name, fatal=False))

        return MediaInfo(
            id=model_name,
            title=title,
            webpage_url=url,
            uploader=model_name,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
