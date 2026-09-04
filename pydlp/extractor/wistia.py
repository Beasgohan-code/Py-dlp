"""Wistia video embed extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class WistiaIE(InfoExtractor):
    """Extractor for Wistia embedded videos."""

    IE_NAME = "wistia"
    IE_DESC = "Wistia.com video embeds"
    _VALID_URL = r"^(?:https?://)?(?:www\.|fast\.)?wistia\.(?:com|net)/(?:embed/iframe|medias)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        # Fetch Wistia media JSON: https://fast.wistia.com/embed/medias/{id}.json
        json_url = f"https://fast.wistia.com/embed/medias/{video_id}.json"
        data = self._download_json(json_url, video_id=video_id, fatal=False)

        title = f"Wistia Video {video_id}"
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if data and "media" in data:
            media = data["media"]
            title = media.get("name", title)
            duration = media.get("duration")
            thumbnail = f"https://fast.wistia.com/embed/medias/{video_id}/thumbnail.jpg"

            assets = media.get("assets", [])
            for a in assets:
                a_url = a.get("url")
                if not a_url:
                    continue
                w = int_or_none(a.get("width"))
                h = int_or_none(a.get("height"))
                size = int_or_none(a.get("size"))
                bitrate = int_or_none(a.get("bitrate"))
                a_type = a.get("type", "")

                formats.append(
                    MediaFormat(
                        format_id=a.get("display_name") or a_type or f"asset-{len(formats)}",
                        url=a_url,
                        ext=a.get("ext", "mp4"),
                        width=w,
                        height=h,
                        filesize=size,
                        tbr=round(bitrate / 1000.0, 1) if bitrate else None,
                        format_note=a.get("display_name"),
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://fast.wistia.net/embed/iframe/{video_id}",
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
