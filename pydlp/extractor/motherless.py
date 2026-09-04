"""Motherless media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class MotherlessIE(InfoExtractor):
    IE_NAME = "motherless"
    IE_DESC = "Motherless video and image extractor"
    _VALID_URL = r"https?://(?:www\.)?motherless\.com/(?:g/[^/]+/)?(?P<id>[A-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        media_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=media_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Motherless {media_id}")
        title = re.sub(r"\s*-\s*Motherless\.com\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        uploader = self._html_search_regex(
            r'class="username"[^>]*>([^<]+)', webpage, "uploader", default=None
        )

        formats: List[MediaFormat] = []

        # Video source extraction
        video_url = self._search_regex(
            [r'setup\(\{\s*file\s*:\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
             r'<source[^>]+src=["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
             r'["\'](https?://cdn\d*\.motherless\.com/videos/[^"\']+)["\']'],
            webpage,
            "video_url",
            default=None,
        )

        if video_url:
            formats.append(
                MediaFormat(
                    format_id="http-direct",
                    url=video_url,
                    ext="mp4",
                    format_note="Direct MP4",
                )
            )

        return MediaInfo(
            id=media_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            uploader=uploader,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
