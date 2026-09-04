"""TnaFlix & EmpFlix media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class TnaFlixIE(InfoExtractor):
    IE_NAME = "tnaflix"
    IE_DESC = "TnaFlix & EmpFlix video extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:tnaflix|empflix)\.com/(?:[^/]+/)?video(?P<id>\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_regex(
            [r'<h1[^>]*>([^<]+)</h1>', r'<meta property="og:title" content="([^"]+)"'],
            webpage,
            "title",
            default=f"TnaFlix Video {video_id}",
        )
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find direct mp4 or m3u8
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        for m in re.finditer(r'<source[^>]+src=["\'](https?://[^"\']+\.mp4[^"\']*)["\'](?:[^>]+res=["\'](\d+)p?["\'])?', webpage):
            src = m.group(1)
            res = m.group(2)
            height = int(res) if res else None
            formats.append(
                MediaFormat(
                    format_id=f"mp4-{res}p" if res else f"mp4-{len(formats)}",
                    url=src,
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
