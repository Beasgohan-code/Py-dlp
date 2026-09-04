"""JWPlayer feed and embed extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class JWPlayerIE(InfoExtractor):
    """Extractor for JWPlayer feeds and embedded video manifests."""

    IE_NAME = "jwplatform"
    IE_DESC = "JWPlayer content manifests and feeds"
    _VALID_URL = r"^(?:https?://)?(?:content|cdn)\.(?:jwplatform|jwplayer)\.com/(?:players|videos|manifests|v2/media)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        media_id = self._match_id(url)
        feed_url = f"https://cdn.jwplayer.com/v2/media/{media_id}"
        feed_data = self._download_json(feed_url, video_id=media_id, fatal=False)

        title = f"JWPlayer Media {media_id}"
        description = None
        duration = None
        thumbnail = f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg"
        formats: List[MediaFormat] = []

        if feed_data:
            title = feed_data.get("title", title)
            description = feed_data.get("description")
            duration = feed_data.get("duration")

            playlist = feed_data.get("playlist", [])
            if playlist:
                item = playlist[0]
                title = item.get("title", title)
                sources = item.get("sources", [])
                for s in sources:
                    s_file = s.get("file")
                    if not s_file:
                        continue
                    s_type = s.get("type", "")
                    if "m3u8" in s_type or ".m3u8" in s_file:
                        formats.extend(self._extract_m3u8_formats(s_file, media_id))
                    else:
                        h = int_or_none(s.get("height"))
                        w = int_or_none(s.get("width"))
                        formats.append(
                            MediaFormat(
                                format_id=s.get("label") or f"http-{h}p" if h else f"mp4-{len(formats)}",
                                url=s_file,
                                ext="mp4",
                                width=w,
                                height=h,
                                format_note=s.get("label"),
                            )
                        )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=media_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://cdn.jwplayer.com/players/{media_id}.html",
            description=description,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
