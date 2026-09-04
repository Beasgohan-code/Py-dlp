"""Kick.com live streams, channels, clips, and VODs extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class KickIE(InfoExtractor):
    """Extractor for Kick.com live streams, clips, and VODs."""

    IE_NAME = "kick"
    IE_DESC = "Kick.com live streams, channels, and clips"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?kick\.com/(?:(?P<channel>[a-zA-Z0-9_-]+)/clips/(?P<clip_id>[a-zA-Z0-9_-]+)|(?P<user>[a-zA-Z0-9_-]+)(?:\?.*)?)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        clip_id = m.group("clip_id")
        channel = m.group("channel") or m.group("user")

        # 1. Clip extraction
        if clip_id:
            api_url = f"https://kick.com/api/v2/clips/{clip_id}"
            clip_data = self._download_json(api_url, video_id=clip_id, fatal=False)

            title = f"Kick Clip {clip_id}"
            thumbnail = None
            formats: List[MediaFormat] = []

            if clip_data:
                clip_obj = clip_data.get("clip", {})
                title = clip_obj.get("title", title)
                thumbnail = clip_obj.get("thumbnail_url")
                video_url = clip_obj.get("video_url")
                if video_url:
                    formats.append(
                        MediaFormat(
                            format_id="clip-hd",
                            url=video_url,
                            ext="mp4",
                            format_note="HD Clip",
                        )
                    )

            if not formats:
                formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

            return MediaInfo(
                id=clip_id,
                title=title,
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=url,
                thumbnail=thumbnail,
                formats=formats,
            )

        # 2. Live Channel extraction
        api_url = f"https://kick.com/api/v2/channels/{channel}"
        channel_data = self._download_json(api_url, video_id=channel, fatal=False)

        title = f"Kick Live - {channel}"
        thumbnail = None
        is_live = False
        formats: List[MediaFormat] = []

        if channel_data:
            livestream = channel_data.get("livestream")
            if livestream:
                is_live = True
                title = livestream.get("session_title", title)
                thumbnail = try_get(livestream, lambda x: x["thumbnail"]["url"], str)
                playback_url = channel_data.get("playback_url")
                if playback_url:
                    formats.extend(self._extract_m3u8_formats(playback_url, channel, note="Live Stream"))

        if not formats:
            # Fallback
            formats.append(
                MediaFormat(
                    format_id="hls-live",
                    url=url,
                    ext="mp4",
                    protocol="m3u8_native",
                )
            )

        return MediaInfo(
            id=channel,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://kick.com/{channel}",
            thumbnail=thumbnail,
            is_live=is_live,
            formats=formats,
        )
