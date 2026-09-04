"""Coursera course lecture and video extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class CourseraIE(InfoExtractor):
    IE_NAME = "coursera"
    IE_DESC = "Coursera course video and lecture extractor"
    _VALID_URL = r"https?://(?:www\.)?coursera\.org/learn/[^/]+/(?:lecture|item)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        lecture_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=lecture_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Coursera Lecture {lecture_id}")
        title = re.sub(r"\s*\|\s*Coursera\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src and "coursera" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=lecture_id, fatal=False))
            elif ".mp4" in src and "coursera" in src:
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=lecture_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
