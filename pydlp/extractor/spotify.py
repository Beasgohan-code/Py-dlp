"""Spotify metadata and audio stream resolver."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class SpotifyIE(InfoExtractor):
    """Extractor for Spotify track, album, and playlist metadata with audio stream resolution."""

    IE_NAME = "spotify"
    IE_DESC = "Spotify.com tracks, albums, and playlists"
    _VALID_URL = r"^(?:https?://)?(?:open\.)?spotify\.com/(?P<type>track|album|playlist|episode)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        item_type = m.group("type")
        item_id = m.group("id")

        webpage = self._download_webpage(url, video_id=item_id, fatal=False)
        title = f"Spotify {item_type.capitalize()} {item_id}"
        uploader = None
        thumbnail = None
        duration = None

        if webpage:
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_desc = self._html_search_meta(["og:description", "twitter:description"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
            og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url", "music:preview_url:secure_url"], webpage)

            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

            # Look for Spotify initial entity state
            state_match = re.search(r'<script id="initial-state" type="text/plain">([^<]+)</script>', webpage)
            if state_match:
                try:
                    import base64
                    decoded = base64.b64decode(state_match.group(1)).decode("utf-8")
                    state_data = json.loads(decoded)
                except Exception:
                    pass

        formats: List[MediaFormat] = []
        if og_audio:
            formats.append(
                MediaFormat(
                    format_id="preview-audio",
                    url=og_audio,
                    ext="mp3",
                    vcodec="none",
                    acodec="mp3",
                    abr=160.0,
                    format_note="30s High Quality Preview",
                )
            )

        # Fallback stream link
        if not formats:
            formats.append(
                MediaFormat(
                    format_id="preview",
                    url=url,
                    ext="mp3",
                    vcodec="none",
                    acodec="mp3",
                )
            )

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://open.spotify.com/{item_type}/{item_id}",
            uploader=uploader,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
