"""BBC iPlayer and BBC News media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class BBCIE(InfoExtractor):
    IE_NAME = "bbc"
    IE_DESC = "BBC iPlayer and BBC News media extractor"
    _VALID_URL = r"https?://(?:www\.)?bbc\.(?:co\.uk|com)/(?:iplayer/episode/|programmes/|news/|sport/)?(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"BBC Video {video_id}")
        title = re.sub(r"\s*-\s*BBC(?:\s*News|\s*iPlayer)?\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find master HLS manifests
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            src = m.group(1)
            if "bbc" in src or "mediaselector" in src or "akamai" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))

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
