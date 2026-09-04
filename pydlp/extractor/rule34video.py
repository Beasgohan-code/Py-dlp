"""Rule34Video, Gelbooru, and Danbooru media extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class Rule34VideoIE(InfoExtractor):
    """Extractor for Rule34Video.party, Gelbooru, and Danbooru media."""

    IE_NAME = "rule34video"
    IE_DESC = "Rule34Video.party and imageboard video extractor"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:rule34video\.party/videos/(?P<id>\d+)|gelbooru\.com/index\.php\?.*?id=(?P<gb_id>\d+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("gb_id")
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"Rule34 Video {video_id}"
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)

            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            if og_video:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext=determine_ext(og_video, "mp4")))

            # HTML5 sources
            src_matches = re.findall(r'<source[^>]+src=["\']([^"\']+)["\'][^>]*title=["\']?([^"\'>]+)?["\']?', webpage)
            for src, res_title in src_matches:
                if src not in [f.url for f in formats]:
                    height = int_or_none(res_title.replace("p", "")) if res_title else None
                    formats.append(
                        MediaFormat(
                            format_id=f"http-{res_title or len(formats)}",
                            url=src,
                            ext=determine_ext(src, "mp4"),
                            height=height,
                            format_note=res_title,
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
