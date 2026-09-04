"""Filemoon and Vidcloud packer decoder."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class FilemoonIE(InfoExtractor):
    """Extractor for Filemoon.sx and Vidcloud videos."""

    IE_NAME = "filemoon"
    IE_DESC = "Filemoon.sx video host"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:filemoon\.(?:sx|to|in|top)|bfst\.(?:to|xyz))/(?:e|d)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        embed_url = f"https://filemoon.sx/e/{video_id}"
        webpage = self._download_webpage(embed_url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Filemoon Video {video_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Look for sources: [{file: "..."}]
            src_matches = re.findall(r'file:\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            for m_url in src_matches:
                formats.extend(self._extract_m3u8_formats(m_url, video_id, headers={"Referer": embed_url}))

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=embed_url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=embed_url,
            thumbnail=thumbnail,
            formats=formats,
        )
