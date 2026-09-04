"""PornTrex media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class PornTrexIE(InfoExtractor):
    IE_NAME = "porntrex"
    IE_DESC = "PornTrex video extractor"
    _VALID_URL = r"https?://(?:www\.)?porntrex\.com/videos/(?P<id>\d+)/?"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"PornTrex Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'video_url\s*:\s*["\'](https?://[^"\']+)["\']', webpage):
            src = m.group(1)
            formats.append(MediaFormat(format_id=f"http-{len(formats)}", url=src, ext="mp4"))

        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
