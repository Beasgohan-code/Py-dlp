"""Audiomack music extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class AudiomackIE(InfoExtractor):
    """Extractor for Audiomack songs and albums."""

    IE_NAME = "audiomack"
    IE_DESC = "Audiomack.com music tracks and albums"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?audiomack\.com/(?P<user>[^/]+)/(?:song|album)/(?P<id>[^/?#]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        user = m.group("user")
        slug = m.group("id")

        webpage = self._download_webpage(url, video_id=slug, fatal=False)
        title = f"Audiomack Track {slug}"
        uploader = user
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url"], webpage)

            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if og_audio:
                formats.append(
                    MediaFormat(
                        format_id="mp3-high",
                        url=og_audio,
                        ext="mp3",
                        vcodec="none",
                        acodec="mp3",
                        abr=320.0,
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp3", vcodec="none", acodec="mp3"))

        return MediaInfo(
            id=slug,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            uploader=uploader,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
