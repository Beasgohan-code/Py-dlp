"""Reddit video and audio extractor (v.redd.it)."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class RedditIE(InfoExtractor):
    """Extractor for Reddit videos and audio."""

    IE_NAME = "reddit"
    IE_DESC = "Reddit.com posts and v.redd.it videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|old\.|v\.)?reddit\.com/(?:r/[^/]+/comments/(?P<id>[a-zA-Z0-9]+)|(?P<vid>[a-zA-Z0-9]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        json_url = f"https://www.reddit.com/comments/{post_id}.json"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        post_data = self._download_json(json_url, video_id=post_id, headers=headers, fatal=False)

        title = f"Reddit Post {post_id}"
        uploader = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if post_data and isinstance(post_data, list) and len(post_data) > 0:
            post = try_get(post_data, lambda x: x[0]["data"]["children"][0]["data"], dict)
            if post:
                title = post.get("title", title)
                uploader = post.get("author")
                thumbnail = post.get("thumbnail")

                media = post.get("media") or post.get("secure_media")
                reddit_video = try_get(media, lambda x: x["reddit_video"], dict)

                if reddit_video:
                    hls_url = reddit_video.get("hls_url")
                    dash_url = reddit_video.get("dash_url")
                    fallback_url = reddit_video.get("fallback_url")
                    duration = reddit_video.get("duration")

                    if hls_url:
                        formats.extend(self._extract_m3u8_formats(hls_url, post_id))

                    if fallback_url:
                        # Construct separate video and audio format pairs
                        width = int_or_none(reddit_video.get("width"))
                        height = int_or_none(reddit_video.get("height"))

                        formats.append(
                            MediaFormat(
                                format_id=f"fallback-{height}p",
                                url=fallback_url,
                                ext="mp4",
                                width=width,
                                height=height,
                                vcodec="h264",
                                acodec="none",
                                format_note=f"{height}p video only",
                            )
                        )

                        # Audio stream
                        base_v_url = fallback_url.rsplit("/", 1)[0]
                        audio_url = f"{base_v_url}/DASH_audio.mp4"
                        formats.append(
                            MediaFormat(
                                format_id="audio-dash",
                                url=audio_url,
                                ext="m4a",
                                vcodec="none",
                                acodec="aac",
                                format_note="Reddit DASH audio",
                            )
                        )

        if not formats:
            # Fallback webpage scraping
            webpage = self._download_webpage(url, video_id=post_id, fatal=False)
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            if og_video:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://www.reddit.com/comments/{post_id}",
            uploader=uploader,
            duration=float(duration) if duration else None,
            thumbnail=thumbnail,
            formats=formats,
        )
