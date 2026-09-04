"""HQPorner and BongaCams video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class HQPornerIE(InfoExtractor):
    """Extractor for HQPorner videos and BongaCams."""

    IE_NAME = "hqporner"
    IE_DESC = "HQPorner.com and BongaCams video extractor"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:hqporner\.com/hdporn/(?P<id>[a-zA-Z0-9_-]+)|bongacams\.com/(?P<bc_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("bc_id")
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"HQPorner Video {video_id}"
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

            # Direct video links in iframe / source
            src_matches = re.findall(r'href=["\'](//(?:media|cdn|video)\.[^"\']+\.mp4[^"\']*)["\']', webpage) + re.findall(
                r'src=["\'](//(?:media|cdn|video)\.[^"\']+\.mp4[^"\']*)["\']', webpage
            )
            for src in src_matches:
                full_src = f"https:{src}" if src.startswith("//") else src
                formats.append(
                    MediaFormat(
                        format_id=f"http-{len(formats)}",
                        url=full_src,
                        ext="mp4",
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
