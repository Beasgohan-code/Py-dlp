"""Vidyard & Brighteon media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class VidyardIE(InfoExtractor):
    IE_NAME = "vidyard"
    IE_DESC = "Vidyard and Brighteon video extractor"
    _VALID_URL = r"https?://(?:(?:share|embed)\.vidyard\.com/watch/(?P<id>[a-zA-Z0-9_-]+)|(?:www\.)?brighteon\.com/(?P<brighteon_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("brighteon_id") or "video"
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Look for HLS or MP4 streams
        for m_hls in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m_hls.group(1), video_id=video_id, fatal=False))

        for m_mp4 in re.finditer(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
            src = m_mp4.group(1)
            if not any(f.url == src for f in formats):
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
