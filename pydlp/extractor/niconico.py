"""NicoNico Douga video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class NiconicoIE(InfoExtractor):
    """Extractor for NicoNico Douga videos."""

    IE_NAME = "niconico"
    IE_DESC = "NicoNico Douga (nicovideo.jp) videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:nicovideo\.jp/watch|nico\.ms)/(?P<id>[a-z]{2}\d+|\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage_url = f"https://www.nicovideo.jp/watch/{video_id}"
        webpage = self._download_webpage(webpage_url, video_id=video_id, fatal=False)

        title = f"NicoNico Video {video_id}"
        thumbnail = None
        duration = None
        uploader = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Look for apiData JSON: data-api-data="..."
            data_match = re.search(r'data-api-data=["\']({.+?})["\']', webpage)
            if data_match:
                try:
                    import html
                    raw_json = html.unescape(data_match.group(1))
                    api_data = json.loads(raw_json)
                    video_data = api_data.get("video", {})
                    title = video_data.get("title", title)
                    thumbnail = try_get(video_data, lambda x: x["thumbnail"]["url"], str) or thumbnail
                    duration = video_data.get("duration")
                    uploader = try_get(api_data, lambda x: x["owner"]["nickname"], str)
                except Exception:
                    pass

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=webpage_url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=webpage_url,
            uploader=uploader,
            thumbnail=thumbnail,
            duration=float(duration) if duration else None,
            formats=formats,
        )
