"""Likee, Triller, and Kwai short video extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class LikeeIE(InfoExtractor):
    IE_NAME = "likee"
    IE_DESC = "Likee, Triller, and Kwai video extractor"
    _VALID_URL = r"https?://(?:(?:www\.|l\.)?likee\.video/@(?P<user>[^/]+)/video/(?P<id>\d+)|(?:www\.)?triller\.co/@(?P<triller_user>[^/]+)/video/(?P<triller_id>[a-zA-Z0-9_-]+)|(?:www\.|m\.)?(?:kwai|kuaishou)\.com/(?:short-video/|photo/)?(?P<kwai_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("triller_id") or m.group("kwai_id") or "video"
        user = m.group("user") or m.group("triller_user") or None

        webpage = self._download_webpage(url, video_id=video_id)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Short Video {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find direct video tag or JSON payload
        for m_src in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m_src.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            uploader=user,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
