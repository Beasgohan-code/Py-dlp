"""Fapello media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class FapelloIE(InfoExtractor):
    IE_NAME = "fapello"
    IE_DESC = "Fapello media extractor"
    _VALID_URL = r"https?://(?:www\.)?fapello\.com/(?P<user>[^/]+)/(?P<id>\d+)/?"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        user = m.group("user") if m else "user"
        media_id = m.group("id") if m else "0"
        full_id = f"{user}_{media_id}"

        webpage = self._download_webpage(url, video_id=full_id)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Fapello {user} {media_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []
        # Find video tag or source
        for m in re.finditer(r'<source[^>]+src=["\'](https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
            formats.append(
                MediaFormat(
                    format_id=f"mp4-{len(formats)}",
                    url=m.group(1),
                    ext="mp4",
                )
            )

        if not formats:
            for m in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
                src = m.group(1)
                if ".m3u8" in src:
                    formats.extend(self._extract_m3u8_formats(src, video_id=full_id, fatal=False))
                elif ".mp4" in src:
                    formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=full_id,
            title=title,
            webpage_url=url,
            uploader=user,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
