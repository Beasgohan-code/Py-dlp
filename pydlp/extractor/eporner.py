"""EPorner 4K and 1080p video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class EpornerIE(InfoExtractor):
    """Extractor for Eporner 4K and HD videos."""

    IE_NAME = "eporner"
    IE_DESC = "EPorner.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?eporner\.com/(?:video-|hd-porn/)(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"EPorner Video {video_id}"
        duration = None
        thumbnail = None
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

            # Query Eporner player JSON API: /xhr/video/{id}
            xhr_url = f"https://www.eporner.com/xhr/video/{video_id}?format=json"
            xhr_data = self._download_json(xhr_url, video_id=video_id, fatal=False)
            if xhr_data and "sources" in xhr_data:
                sources = xhr_data.get("sources", {})
                for res_key, s_data in sources.items():
                    s_url = s_data.get("src") if isinstance(s_data, dict) else s_data
                    if s_url:
                        height = int_or_none(res_key.replace("p", "").replace("k", ""))
                        formats.append(
                            MediaFormat(
                                format_id=f"http-{res_key}",
                                url=s_url,
                                ext="mp4",
                                height=height,
                                format_note=res_key,
                            )
                        )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            duration=duration,
            age_limit=18,
            formats=formats,
        )
