"""TuneIn Radio live audio stream extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class TuneInIE(InfoExtractor):
    IE_NAME = "tunein"
    IE_DESC = "TuneIn Radio live audio stream extractor"
    _VALID_URL = r"https?://(?:www\.)?tunein\.com/(?:radio/|podcasts/)?(?P<id>[a-zA-Z0-9_.-]+-s\d+|[a-zA-Z0-9_.-]+-p\d+|s\d+|p\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        station_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=station_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"TuneIn Station {station_id}")
        title = re.sub(r"\s*\|\s*TuneIn\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp3|aac|pls)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=station_id, fatal=False))
            elif not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"audio-{len(formats)}", url=src, ext="mp3", vcodec="none"))

        return MediaInfo(
            id=station_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
