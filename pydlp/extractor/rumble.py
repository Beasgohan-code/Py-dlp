"""Rumble video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class RumbleIE(InfoExtractor):
    """Extractor for Rumble videos."""

    IE_NAME = "rumble"
    IE_DESC = "Rumble.com videos and live streams"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?rumble\.com/(?:v(?P<id>[a-zA-Z0-9]+)-|embed/(?P<embed_id>[a-zA-Z0-9]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"Rumble Video {video_id}"
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        # Find Rumble embedded video config JSON (Rumble.embed or json-ld)
        config_match = re.search(r'Rumble\(\s*["\']play["\'],\s*({.+?})\s*\);', webpage)
        if config_match:
            try:
                data = json.loads(config_match.group(1))
                title = data.get("title", title)
                duration = data.get("duration")
                thumbnail = data.get("i")

                # Video streams (u = mp4 video streams, ua = adaptive)
                u = data.get("u", {})
                for res_key, stream_info in u.items():
                    s_url = stream_info.get("url")
                    if s_url:
                        height = int_or_none(res_key.replace("p", ""))
                        formats.append(
                            MediaFormat(
                                format_id=f"http-{res_key}",
                                url=s_url,
                                ext="mp4",
                                height=height,
                                format_note=res_key,
                            )
                        )
            except Exception:
                pass

        if not formats:
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
