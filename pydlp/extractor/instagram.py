"""Instagram post, reel, story, and carousel extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class InstagramIE(InfoExtractor):
    """Extractor for Instagram posts, reels, and stories."""

    IE_NAME = "instagram"
    IE_DESC = "Instagram.com posts, reels, and TV videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|tv)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        shortcode = self._match_id(url)
        webpage = self._download_webpage(url, video_id=shortcode, fatal=False)

        title = f"Instagram Post {shortcode}"
        description = None
        uploader = None
        thumbnail = None
        formats: List[MediaFormat] = []

        # 1. Search embedded sharedData or additionalData
        shared_data_match = re.search(r"_sharedData\s*=\s*({.+?});</script>", webpage)
        if shared_data_match:
            try:
                data = json.loads(shared_data_match.group(1))
                media = try_get(
                    data,
                    lambda x: x["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"],
                    dict,
                )
                if media:
                    title = try_get(media, lambda x: x["edge_media_to_caption"]["edges"][0]["node"]["text"], str) or title
                    uploader = try_get(media, lambda x: x["owner"]["username"], str)
                    video_url = media.get("video_url")
                    thumbnail = media.get("display_url")
                    if video_url:
                        formats.append(
                            MediaFormat(
                                format_id="hd",
                                url=video_url,
                                ext="mp4",
                                width=int_or_none(try_get(media, lambda x: x["dimensions"]["width"])),
                                height=int_or_none(try_get(media, lambda x: x["dimensions"]["height"])),
                            )
                        )
            except Exception:
                pass

        # 2. OpenGraph Fallbacks
        if not formats:
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            og_title = self._html_search_meta(["og:title"], webpage)
            og_desc = self._html_search_meta(["og:description"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_video:
                formats.append(
                    MediaFormat(
                        format_id="og-video",
                        url=og_video,
                        ext="mp4",
                    )
                )
            if og_title:
                title = og_title
            if og_desc:
                description = og_desc
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=shortcode,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            thumbnail=thumbnail,
            formats=formats,
        )
