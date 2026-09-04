"""Bluesky social video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class BlueskyIE(InfoExtractor):
    """Extractor for Bluesky ATProto video embeds and clips."""

    IE_NAME = "bluesky"
    IE_DESC = "Bluesky (bsky.app) video posts"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?bsky\.app/profile/(?P<user>[^/]+)/post/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, fatal=False)

        title = f"Bluesky Post {post_id}"
        description = None
        thumbnail = None
        formats: List[MediaFormat] = []

        # Bluesky video HLS video stream format: https://video.bsky.app/watch/did%3Aplc.../playlist.m3u8
        hls_match = re.search(r'(https://video\.bsky\.app/watch/[^"\'\s]+/playlist\.m3u8)', webpage)
        if hls_match:
            formats.extend(self._extract_m3u8_formats(hls_match.group(1), post_id))

        og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
        og_title = self._html_search_meta(["og:title"], webpage)
        og_desc = self._html_search_meta(["og:description"], webpage)
        og_thumb = self._html_search_meta(["og:image"], webpage)

        if og_video and not formats:
            if ".m3u8" in og_video:
                formats.extend(self._extract_m3u8_formats(og_video, post_id))
            else:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))

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
            thumbnail=thumbnail,
            formats=formats,
        )
