"""SoundCloud track and playlist extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class SoundCloudIE(InfoExtractor):
    """Extractor for SoundCloud tracks and playlists."""

    IE_NAME = "soundcloud"
    IE_DESC = "SoundCloud.com tracks and sets"
    _VALID_URL = r"^(?:https?://)?(?:www\.|m\.)?soundcloud\.com/(?P<user>[^/]+)/(?P<id>[^/?#]+)"

    _CLIENT_ID = "iZIs9mchVcX5lhVR1pnZW1e9Z2nsQNtt"

    def _real_extract(self, url: str) -> MediaInfo:
        track_slug = self._match_id(url)
        webpage = self._download_webpage(url, video_id=track_slug, fatal=False)

        title = f"SoundCloud Track {track_slug}"
        description = None
        uploader = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        # Find hydration data embedded in __sc_hydration
        hydration_match = re.search(r"window\.__sc_hydration\s*=\s*(\[.+?\]);", webpage)
        if hydration_match:
            try:
                hydration_data = json.loads(hydration_match.group(1))
                for item in hydration_data:
                    if item.get("hydratable") == "sound":
                        sound_data = item.get("data", {})
                        title = sound_data.get("title", title)
                        description = sound_data.get("description")
                        uploader = try_get(sound_data, lambda x: x["user"]["username"], str)
                        thumbnail = sound_data.get("artwork_url") or try_get(sound_data, lambda x: x["user"]["avatar_url"], str)
                        duration = sound_data.get("duration", 0) / 1000.0

                        media = sound_data.get("media", {})
                        transcodings = media.get("transcodings", [])
                        for t in transcodings:
                            t_url = t.get("url")
                            preset = t.get("preset", "")
                            format_protocol = try_get(t, lambda x: x["format"]["protocol"], str) or "progressive"
                            mime = try_get(t, lambda x: x["format"]["mime_type"], str) or ""

                            # Query stream URL
                            if t_url:
                                stream_info = self._download_json(
                                    f"{t_url}?client_id={self._CLIENT_ID}&track_authorization={sound_data.get('track_authorization', '')}",
                                    video_id=track_slug,
                                    fatal=False,
                                )
                                direct_stream = stream_info.get("url") if stream_info else None
                                if direct_stream:
                                    ext = "mp3" if "audio/mpeg" in mime else ("opus" if "ogg" in mime else "mp3")
                                    if "hls" in format_protocol:
                                        formats.extend(self._extract_m3u8_formats(direct_stream, track_slug, ext=ext, note=preset))
                                    else:
                                        formats.append(
                                            MediaFormat(
                                                format_id=f"http-{preset}",
                                                url=direct_stream,
                                                ext=ext,
                                                vcodec="none",
                                                acodec=ext,
                                                format_note=preset,
                                            )
                                        )
            except Exception:
                pass

        # Fallbacks
        if not formats:
            og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url", "twitter:player:stream"], webpage)
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
            if og_audio:
                formats.append(MediaFormat(format_id="og-audio", url=og_audio, ext="mp3", vcodec="none", acodec="mp3"))
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=track_slug,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            duration=duration,
            thumbnail=thumbnail,
            formats=formats,
        )
