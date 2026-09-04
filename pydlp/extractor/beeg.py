"""Beeg media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class BeegIE(InfoExtractor):
    IE_NAME = "beeg"
    IE_DESC = "Beeg.com video extractor"
    _VALID_URL = r"https?://(?:www\.)?beeg\.com/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Beeg Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find m3u8 or mp4 sources
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        for m in re.finditer(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
            formats.append(
                MediaFormat(
                    format_id=f"mp4-{len(formats)}",
                    url=m.group(1),
                    ext="mp4",
                )
            )

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
