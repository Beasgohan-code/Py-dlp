"""Threads post and video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class ThreadsIE(InfoExtractor):
    """Extractor for Meta Threads posts and videos."""

    IE_NAME = "threads"
    IE_DESC = "Threads.net posts and videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?threads\.net/(?:@[^/]+/post/(?P<id>[a-zA-Z0-9_-]+)|t/(?P<tid>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Threads Post {post_id}"
        description = None
        uploader = None
        thumbnail = None
        formats: List[MediaFormat] = []

        og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
        og_title = self._html_search_meta(["og:title"], webpage)
        og_desc = self._html_search_meta(["og:description"], webpage)
        og_thumb = self._html_search_meta(["og:image"], webpage)

        if og_video:
            formats.append(MediaFormat(format_id="hd", url=og_video, ext="mp4"))
        if og_title:
            title = og_title
        if og_desc:
            description = og_desc
        if og_thumb:
            thumbnail = og_thumb

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            thumbnail=thumbnail,
            formats=formats,
        )
