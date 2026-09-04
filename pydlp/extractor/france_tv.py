"""France.tv, TF1+, and 6play media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class FranceTVIE(InfoExtractor):
    IE_NAME = "francetv"
    IE_DESC = "France.tv, TF1+, and 6play French media extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:france\.tv|tf1\.fr|6play\.fr)/(?:[^/]+/)*(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"French TV {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
