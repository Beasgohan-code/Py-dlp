"""9GAG media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class NineGagIE(InfoExtractor):
    IE_NAME = "9gag"
    IE_DESC = "9GAG video and post extractor"
    _VALID_URL = r"https?://(?:www\.)?9gag\.com/gag/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"9GAG {post_id}")
        title = re.sub(r"\s*-\s*9GAG\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find 9GAG video sources (.mp4, .webm)
        for m in re.finditer(r'["\'](https?://[^"\']*(?:9cache\.com|9gag\.com)/[^"\']+\.(?:mp4|webm))["\']', webpage):
            src = m.group(1)
            ext = "mp4" if ".mp4" in src else "webm"
            if not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"9gag-{ext}", url=src, ext=ext))

        return MediaInfo(
            id=post_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
