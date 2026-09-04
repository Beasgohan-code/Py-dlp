"""Giphy media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class GiphyIE(InfoExtractor):
    IE_NAME = "giphy"
    IE_DESC = "Giphy GIF and MP4 extractor"
    _VALID_URL = r"https?://(?:www\.|media\.)?giphy\.com/(?:gifs|media)/(?:[^/]+-)?(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        gif_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=gif_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Giphy {gif_id}")
        title = re.sub(r"\s*-\s*Find & Share on GIPHY\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find mp4 video or webm
        for m in re.finditer(r'["\'](https?://media\d*\.giphy\.com/media/[^"\']+\.(?:mp4|webm|gif))["\']', webpage):
            src = m.group(1)
            ext = "mp4" if ".mp4" in src else ("webm" if ".webm" in src else "gif")
            if not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"media-{ext}", url=src, ext=ext))

        if not formats:
            formats.append(
                MediaFormat(
                    format_id="mp4-direct",
                    url=f"https://media.giphy.com/media/{gif_id}/giphy.mp4",
                    ext="mp4",
                )
            )

        return MediaInfo(
            id=gif_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
