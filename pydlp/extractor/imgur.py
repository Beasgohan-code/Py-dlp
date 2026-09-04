"""Imgur media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class ImgurIE(InfoExtractor):
    IE_NAME = "imgur"
    IE_DESC = "Imgur image, video, and GIF extractor"
    _VALID_URL = r"https?://(?:i\.)?imgur\.com/(?:gallery/|a/)?(?P<id>[a-zA-Z0-9]+)(?:\.[a-zA-Z0-9]+)?"

    def _real_extract(self, url: str) -> MediaInfo:
        media_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=media_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Imgur {media_id}")
        title = re.sub(r"\s*-\s*Imgur\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find direct mp4 or gifv
        for m in re.finditer(r'["\'](https?://i\.imgur\.com/[a-zA-Z0-9]+\.(?:mp4|webm|gif))["\']', webpage):
            src = m.group(1)
            ext = "mp4" if ".mp4" in src else ("webm" if ".webm" in src else "gif")
            if not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"http-{ext}", url=src, ext=ext))

        # Standard direct URL fallback
        if not formats:
            formats.append(
                MediaFormat(
                    format_id="mp4-direct",
                    url=f"https://i.imgur.com/{media_id}.mp4",
                    ext="mp4",
                )
            )

        return MediaInfo(
            id=media_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
