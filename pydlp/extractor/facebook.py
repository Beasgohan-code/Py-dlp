"""Facebook video extractor."""

from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, unescape_html
from pydlp.extractor.base import InfoExtractor


class FacebookIE(InfoExtractor):
    """Extractor for Facebook public videos and reels."""

    IE_NAME = "facebook"
    IE_DESC = "Facebook.com public videos, reels, and watch clips"
    _VALID_URL = r"^(?:https?://)?(?:www\.|m\.|web\.)?facebook\.com/(?:video\.php\?v=|watch/\?v=|[^/]+/videos/|reel/)(?P<id>\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Facebook Video {video_id}"
        description = None
        thumbnail = None
        formats: List[MediaFormat] = []

        # Find progressive SD / HD video links
        sd_match = re.search(r'["\']browser_native_sd_url["\']\s*:\s*["\']([^"\']+)["\']', webpage) or re.search(r'sd_src\s*:\s*["\']([^"\']+)["\']', webpage)
        hd_match = re.search(r'["\']browser_native_hd_url["\']\s*:\s*["\']([^"\']+)["\']', webpage) or re.search(r'hd_src\s*:\s*["\']([^"\']+)["\']', webpage)

        if sd_match:
            sd_url = sd_match.group(1).replace(r"\/", "/")
            formats.append(
                MediaFormat(
                    format_id="sd",
                    url=sd_url,
                    ext="mp4",
                    format_note="SD",
                )
            )

        if hd_match:
            hd_url = hd_match.group(1).replace(r"\/", "/")
            formats.append(
                MediaFormat(
                    format_id="hd",
                    url=hd_url,
                    ext="mp4",
                    format_note="HD",
                )
            )

        og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
        if og_video and not formats:
            formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))

        og_title = self._html_search_meta(["og:title"], webpage)
        og_desc = self._html_search_meta(["og:description"], webpage)
        og_thumb = self._html_search_meta(["og:image"], webpage)

        if og_title:
            title = og_title
        if og_desc:
            description = og_desc
        if og_thumb:
            thumbnail = og_thumb

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            formats=formats,
        )
