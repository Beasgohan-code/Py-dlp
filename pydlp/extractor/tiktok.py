"""TikTok video and user media extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class TikTokIE(InfoExtractor):
    """Extractor for TikTok videos."""

    IE_NAME = "tiktok"
    IE_DESC = "TikTok.com videos and sounds"
    _VALID_URL = r"^(?:https?://)?(?:www\.|m\.|t\.)?tiktok\.com/(?:@(?P<user>[^/]+)/video/(?P<id>\d+)|v/(?P<vid>\d+)|(?P<shortid>[\w-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"TikTok Video {video_id}"
        description = None
        uploader = None
        uploader_id = None
        thumbnail = None
        formats: List[MediaFormat] = []

        # 1. Look for SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
        sigi_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">([^<]+)</script>', webpage)
        if not sigi_match:
            sigi_match = re.search(r'<script id="SIGI_STATE" type="application/json">([^<]+)</script>', webpage)

        if sigi_match:
            try:
                data = json.loads(sigi_match.group(1))
                item_struct = (
                    try_get(data, lambda x: x["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"], dict)
                    or try_get(data, lambda x: x["ItemModule"][video_id], dict)
                )
                if item_struct:
                    title = item_struct.get("desc") or title
                    description = item_struct.get("desc")
                    uploader = try_get(item_struct, lambda x: x["author"]["nickname"], str)
                    uploader_id = try_get(item_struct, lambda x: x["author"]["uniqueId"], str)

                    video_data = item_struct.get("video", {})
                    thumbnail = video_data.get("cover") or video_data.get("originCover")
                    play_addr = video_data.get("playAddr") or video_data.get("downloadAddr")
                    width = int_or_none(video_data.get("width"))
                    height = int_or_none(video_data.get("height"))
                    ratio = video_data.get("ratio")

                    if play_addr:
                        formats.append(
                            MediaFormat(
                                format_id="hd-nowatermark",
                                url=play_addr,
                                ext="mp4",
                                width=width,
                                height=height,
                                format_note="No Watermark HD",
                                http_headers={"Referer": "https://www.tiktok.com/"},
                            )
                        )

                    # Music audio
                    music_data = item_struct.get("music", {})
                    music_url = music_data.get("playUrl")
                    if music_url:
                        formats.append(
                            MediaFormat(
                                format_id="audio-only",
                                url=music_url,
                                ext="mp3",
                                vcodec="none",
                                acodec="mp3",
                                format_note="Original Sound",
                            )
                        )
            except Exception:
                pass

        if not formats:
            # Fallback to OpenGraph
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
            if og_video:
                formats.append(
                    MediaFormat(
                        format_id="download",
                        url=og_video,
                        ext="mp4",
                        http_headers={"Referer": "https://www.tiktok.com/"},
                    )
                )
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            uploader_id=uploader_id,
            thumbnail=thumbnail,
            formats=formats,
        )
