"""Dailymotion video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class DailymotionIE(InfoExtractor):
    """Extractor for Dailymotion videos."""

    IE_NAME = "dailymotion"
    IE_DESC = "Dailymotion.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|touch\.)?dailymotion\.com/(?:video|embed/video)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        metadata_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
        meta = self._download_json(metadata_url, video_id=video_id, fatal=False)

        title = f"Dailymotion Video {video_id}"
        uploader = None
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if meta:
            title = meta.get("title", title)
            uploader = meta.get("owner", {}).get("screenname")
            duration = meta.get("duration")
            thumbnail = meta.get("posters", {}).get("60") or meta.get("posters", {}).get("480")

            qualities = meta.get("qualities", {})
            for q_name, stream_list in qualities.items():
                for stream in stream_list:
                    s_type = stream.get("type", "")
                    s_url = stream.get("url")
                    if "mpegurl" in s_type and s_url:
                        formats.extend(self._extract_m3u8_formats(s_url, video_id, note=q_name))
                    elif "mp4" in s_type and s_url:
                        formats.append(
                            MediaFormat(
                                format_id=f"http-{q_name}",
                                url=s_url,
                                ext="mp4",
                                format_note=q_name,
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
            webpage_url=f"https://www.dailymotion.com/video/{video_id}",
            uploader=uploader,
            duration=float(duration) if duration else None,
            thumbnail=thumbnail,
            formats=formats,
        )
