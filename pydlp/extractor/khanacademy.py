"""Khan Academy video extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class KhanAcademyIE(InfoExtractor):
    IE_NAME = "khanacademy"
    IE_DESC = "Khan Academy educational lessons extractor"
    _VALID_URL = r"https?://(?:www\.)?khanacademy\.org/(?:[a-z0-9_-]+/)+v/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        lesson_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=lesson_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Khan Academy {lesson_id}")
        title = re.sub(r"\s*\(video\)\s*\|\s*Khan Academy\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        # Khan Academy often embeds YouTube videos or mp4
        yt_id = self._search_regex(r'youtubeId["\']\s*:\s*["\']([a-zA-Z0-9_-]{11})["\']', webpage, "youtube_id", default=None)
        if yt_id:
            formats.append(MediaFormat(format_id="youtube-embed", url=f"https://www.youtube.com/watch?v={yt_id}", ext="mp4"))

        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src and "khanacademy" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=lesson_id, fatal=False))
            elif ".mp4" in src and "khanacademy" in src:
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=lesson_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
