"""VK and VK Video extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none, parse_duration, unescape_html
from pydlp.extractor.base import InfoExtractor


class VKIE(InfoExtractor):
    IE_NAME = "vk"
    IE_DESC = "VK.com and VK Video media extractor"
    _VALID_URL = r"https?://(?:www\.|m\.)?(?:vk\.com|vkvideo\.ru)/(?:video|clip|wall)?(?P<id>-?\d+_\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"VK Video {video_id}")
        title = re.sub(r"\s*\|\s*ВКонтакте\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Check for HLS manifest (.m3u8)
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        # Check for direct mp4 urls in player variables (e.g. url240, url360, url480, url720, url1080)
        for m in re.finditer(r'["\']url(\d+)["\']\s*:\s*["\'](https?://[^"\']+)["\']', webpage):
            height = int(m.group(1))
            video_url = unescape_html(m.group(2)).replace(r"\/", "/")
            formats.append(
                MediaFormat(
                    format_id=f"mp4-{height}p",
                    url=video_url,
                    ext="mp4",
                    height=height,
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
