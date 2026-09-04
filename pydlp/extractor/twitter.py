"""Twitter / X status video and media extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_iso8601, try_get
from pydlp.extractor.base import InfoExtractor


class TwitterIE(InfoExtractor):
    """Extractor for Twitter / X tweets and media clips."""

    IE_NAME = "twitter"
    IE_DESC = "Twitter / X tweet videos and GIFs"
    _VALID_URL = r"^(?:https?://)?(?:www\.|mobile\.)?(?:twitter|x)\.com/(?:i/web|[^/]+)/status/(?P<id>\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        status_id = self._match_id(url)

        # Query Twitter Syndication API (publicly accessible JSON endpoint)
        syndication_url = f"https://cdn.syndication.twimg.com/tweet-result?id={status_id}&token=x"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
            "Referer": "https://platform.twitter.com/",
        }
        tweet_data = self._download_json(syndication_url, video_id=status_id, headers=headers, fatal=False)

        title = f"Twitter Post {status_id}"
        description = None
        uploader = None
        uploader_id = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if tweet_data:
            text = tweet_data.get("text")
            if text:
                title = text.split("\n")[0][:100]
                description = text

            user = tweet_data.get("user", {})
            uploader = user.get("name")
            uploader_id = user.get("screen_name")

            media_entities = tweet_data.get("mediaDetails", []) or tweet_data.get("entities", {}).get("media", [])
            for media in media_entities:
                video_info = media.get("video_info")
                if video_info:
                    variants = video_info.get("variants", [])
                    for var in variants:
                        v_url = var.get("url")
                        content_type = var.get("content_type", "")
                        bitrate = int_or_none(var.get("bitrate"))

                        if "mp4" in content_type and v_url:
                            # Extract resolution from URL if available (e.g. /720x1280/)
                            res_m = re.search(r"/(\d+)x(\d+)/", v_url)
                            w = int(res_m.group(1)) if res_m else None
                            h = int(res_m.group(2)) if res_m else None

                            formats.append(
                                MediaFormat(
                                    format_id=f"http-{bitrate or len(formats)}",
                                    url=v_url,
                                    ext="mp4",
                                    width=w,
                                    height=h,
                                    tbr=round(bitrate / 1000.0, 1) if bitrate else None,
                                    format_note=f"{h}p" if h else None,
                                )
                            )
                        elif "x-mpegURL" in content_type and v_url:
                            formats.extend(self._extract_m3u8_formats(v_url, status_id))

                    thumbnail = media.get("media_url_https") or thumbnail

        if not formats:
            # Fallback webpage scraping
            webpage = self._download_webpage(url, video_id=status_id, fatal=False)
            og_video = self._html_search_meta(["og:video", "og:video:secure_url", "twitter:player:stream"], webpage)
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
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
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=status_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://x.com/i/status/{status_id}",
            description=description,
            uploader=uploader,
            uploader_id=uploader_id,
            thumbnail=thumbnail,
            formats=formats,
        )
