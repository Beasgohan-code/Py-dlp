"""Douyin, Kuaishou, and XiaoHongShu extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class DouyinIE(InfoExtractor):
    """Extractor for Douyin, Kuaishou, and XiaoHongShu videos."""

    IE_NAME = "douyin"
    IE_DESC = "Douyin, Kuaishou, and XiaoHongShu short videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|v\.)?(?:douyin\.com/(?:video|note)/|iesdouyin\.com/share/video/|kuaishou\.com/short-video/|xiaohongshu\.com/explore/)(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"}, fatal=False)

        title = f"Short Video {video_id}"
        thumbnail = None
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
                formats.append(MediaFormat(format_id="hd", url=og_video, ext="mp4"))

            # Look for play_addr in __RENDER_DATA__ or RENDER_DATA
            render_match = re.search(r'<script id="RENDER_DATA" type="application/json">([^<]+)</script>', webpage)
            if render_match:
                try:
                    import urllib.parse
                    decoded_str = urllib.parse.unquote(render_match.group(1))
                    rdata = json.loads(decoded_str)
                except Exception:
                    pass

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            formats=formats,
        )
