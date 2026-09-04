"""NHK World Japan media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class NHKIE(InfoExtractor):
    IE_NAME = "nhk"
    IE_DESC = "NHK World Japan media extractor"
    _VALID_URL = r"https?://(?:www\.)?nhk\.(?:or\.jp|jp)/(?:nhkworld/[a-z]{2}/ondemand/video/|ondemand/program/)?(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"NHK Video {video_id}")
        title = re.sub(r"\s*\|\s*NHK WORLD-JAPAN\s*$", "", title).strip()
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
