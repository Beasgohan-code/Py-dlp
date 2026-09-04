"""Tidal media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class TidalIE(InfoExtractor):
    IE_NAME = "tidal"
    IE_DESC = "Tidal.com track and video extractor"
    _VALID_URL = r"https?://(?:www\.|listen\.)?tidal\.com/(?:browse/)?(?:track|video|album)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        track_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=track_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Tidal Track {track_id}")
        title = re.sub(r"\s*on TIDAL\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find audio preview or streaming manifests
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4|m4a|mp3|flac)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=track_id, fatal=False))
            elif ".mp4" in src or ".m4a" in src or ".mp3" in src:
                formats.append(
                    MediaFormat(
                        format_id=f"audio-{len(formats)}",
                        url=src,
                        ext="m4a" if ".m4a" in src else "mp3",
                        vcodec="none",
                    )
                )

        return MediaInfo(
            id=track_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
