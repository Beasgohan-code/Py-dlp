"""Cumlouder & Daftsex media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class CumlouderIE(InfoExtractor):
    IE_NAME = "cumlouder"
    IE_DESC = "Cumlouder & Daftsex video extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:cumlouder\.com/(?:[a-z]{2}/)?(?:video/|porn-video/)(?P<id>[^/?#&]+)|daftsex\.com/watch/(?P<daft_id>[^/?#&]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("daft_id") or "video"
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m_src in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m_src.group(1)
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
