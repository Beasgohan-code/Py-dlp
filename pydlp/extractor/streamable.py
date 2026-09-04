"""Streamable video clip extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class StreamableIE(InfoExtractor):
    """Extractor for Streamable videos."""

    IE_NAME = "streamable"
    IE_DESC = "Streamable.com video clips"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?streamable\.com/(?:[a-z]{2}/)?(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        api_url = f"https://api.streamable.com/videos/{video_id}"
        meta = self._download_json(api_url, video_id=video_id, fatal=False)

        title = f"Streamable Video {video_id}"
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if meta:
            title = meta.get("title") or title
            duration = meta.get("duration")
            thumbnail = meta.get("thumbnail_url")
            if thumbnail and thumbnail.startswith("//"):
                thumbnail = f"https:{thumbnail}"

            files = meta.get("files", {})
            for quality_name, file_info in files.items():
                s_url = file_info.get("url")
                if s_url:
                    if s_url.startswith("//"):
                        s_url = f"https:{s_url}"
                    width = int_or_none(file_info.get("width"))
                    height = int_or_none(file_info.get("height"))
                    size = int_or_none(file_info.get("size"))
                    bitrate = int_or_none(file_info.get("bitrate"))

                    formats.append(
                        MediaFormat(
                            format_id=quality_name,
                            url=s_url,
                            ext="mp4",
                            width=width,
                            height=height,
                            filesize=size,
                            tbr=round(bitrate / 1000.0, 1) if bitrate else None,
                            format_note=quality_name,
                        )
                    )

        if not formats:
            webpage = self._download_webpage(url, video_id=video_id, fatal=False)
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_video:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            duration=float(duration) if duration else None,
            thumbnail=thumbnail,
            formats=formats,
        )
