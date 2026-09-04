"""Mixlr live broadcast audio extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class MixlrIE(InfoExtractor):
    IE_NAME = "mixlr"
    IE_DESC = "Mixlr live broadcast audio extractor"
    _VALID_URL = r"https?://(?:www\.)?mixlr\.com/(?P<id>[a-zA-Z0-9_-]+)(?:/showcase/[^/?#&]+)?"

    def _real_extract(self, url: str) -> MediaInfo:
        user_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=user_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Mixlr Broadcast {user_id}")
        title = re.sub(r"\s*is on Mixlr\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp3|aac)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=user_id, fatal=False))
            elif not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"audio-{len(formats)}", url=src, ext="mp3", vcodec="none"))

        return MediaInfo(
            id=user_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
