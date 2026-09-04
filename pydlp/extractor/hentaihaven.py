"""HentaiHaven media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class HentaiHavenIE(InfoExtractor):
    IE_NAME = "hentaihaven"
    IE_DESC = "HentaiHaven anime & video extractor"
    _VALID_URL = r"https?://(?:www\.)?hentaihaven\.(?:xxx|com|red|me)/(?:episode/|watch/)?(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"HentaiHaven {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find iframe embeds or player sources
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            stream_url = m.group(1)
            if ".m3u8" in stream_url:
                formats.extend(self._extract_m3u8_formats(stream_url, video_id=video_id, fatal=False))
            elif ".mp4" in stream_url:
                formats.append(
                    MediaFormat(
                        format_id=f"mp4-{len(formats)}",
                        url=stream_url,
                        ext="mp4",
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
