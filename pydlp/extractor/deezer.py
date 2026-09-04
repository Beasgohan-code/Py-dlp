"""Deezer track and album extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class DeezerIE(InfoExtractor):
    """Extractor for Deezer music tracks and albums."""

    IE_NAME = "deezer"
    IE_DESC = "Deezer.com music tracks and albums"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?deezer\.com/(?:[a-z]{2}/)?(?P<type>track|album|playlist)/(?P<id>\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        item_type = m.group("type")
        item_id = m.group("id")

        api_url = f"https://api.deezer.com/{item_type}/{item_id}"
        data = self._download_json(api_url, video_id=item_id, fatal=False)

        title = f"Deezer Track {item_id}"
        uploader = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if data:
            title = data.get("title") or data.get("name") or title
            duration = data.get("duration")
            uploader = try_get(data, lambda x: x["artist"]["name"], str)
            thumbnail = try_get(data, lambda x: x["album"]["cover_big"], str) or data.get("picture_big")

            preview_url = data.get("preview")
            if preview_url:
                formats.append(
                    MediaFormat(
                        format_id="preview",
                        url=preview_url,
                        ext="mp3",
                        vcodec="none",
                        acodec="mp3",
                        abr=128.0,
                        format_note="MP3 Preview",
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp3", vcodec="none", acodec="mp3"))

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://www.deezer.com/{item_type}/{item_id}",
            uploader=uploader,
            thumbnail=thumbnail,
            duration=float(duration) if duration else None,
            formats=formats,
        )
