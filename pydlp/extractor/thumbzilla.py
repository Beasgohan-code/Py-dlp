"""Thumbzilla media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class ThumbzillaIE(InfoExtractor):
    IE_NAME = "thumbzilla"
    IE_DESC = "Thumbzilla.com video extractor"
    _VALID_URL = r"https?://(?:www\.)?thumbzilla\.com/video/(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Thumbzilla {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Parse player JSON config or flashvars
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                res_m = re.search(r'(\d+)p', src)
                height = int(res_m.group(1)) if res_m else None
                formats.append(MediaFormat(format_id=f"mp4-{height}p" if height else f"mp4-{len(formats)}", url=src, ext="mp4", height=height))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
