"""Loom video recording extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class LoomIE(InfoExtractor):
    """Extractor for Loom video recordings."""

    IE_NAME = "loom"
    IE_DESC = "Loom.com video recordings"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?loom\.com/(?:share|embed)/(?P<id>[a-f0-9]{32})"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        # Query Loom internal graphql or public session API
        api_url = f"https://www.loom.com/api/campaigns/sessions/{video_id}/transcoded-url"
        session_info = self._download_json(api_url, video_id=video_id, data=b"{}", headers={"Content-Type": "application/json"}, fatal=False)

        webpage = self._download_webpage(f"https://www.loom.com/share/{video_id}", video_id=video_id, fatal=False)

        title = f"Loom Recording {video_id}"
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            dur_str = self._html_search_meta(["video:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if dur_str:
                duration = parse_duration(dur_str)

        if session_info and "url" in session_info:
            direct_url = session_info["url"]
            if ".m3u8" in direct_url:
                formats.extend(self._extract_m3u8_formats(direct_url, video_id))
            else:
                formats.append(MediaFormat(format_id="loom-hd", url=direct_url, ext="mp4"))

        if not formats:
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            if og_video:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))
            else:
                formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://www.loom.com/share/{video_id}",
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
