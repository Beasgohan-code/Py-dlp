"""Arte.tv European cultural television extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class ArteTVIE(InfoExtractor):
    IE_NAME = "arte"
    IE_DESC = "Arte.tv European cultural network extractor"
    _VALID_URL = r"https?://(?:www\.)?arte\.tv/(?:[a-z]{2}/)?videos/(?P<id>[0-9A-Z-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Arte TV {video_id}")
        title = re.sub(r"\s*\|\s*ARTE\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find HLS stream manifests or direct mp4 sources
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src and "arte" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))
            elif ".mp4" in src and "arte" in src:
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

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
