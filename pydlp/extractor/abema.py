"""AbemaTV series and episode extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class AbemaIE(InfoExtractor):
    """Extractor for AbemaTV (abema.tv) series, episodes, and live channels."""

    IE_NAME = "abema"
    IE_DESC = "AbemaTV series and episodes"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?abema\.tv/(?:channels/[^/]+/slots/|video/episode/|video/title/)(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        item_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=item_id, fatal=False)

        title = f"AbemaTV Video {item_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Look for m3u8 playlist links in json or script
            m3u8_matches = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            for m_url in m3u8_matches:
                formats.extend(self._extract_m3u8_formats(m_url, item_id, note="HLS"))

        if not formats:
            formats.append(MediaFormat(format_id="hls-default", url=url, ext="mp4", protocol="m3u8_native"))

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            formats=formats,
        )
