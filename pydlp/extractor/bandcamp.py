"""Bandcamp track and album extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class BandcampIE(InfoExtractor):
    """Extractor for Bandcamp tracks and albums."""

    IE_NAME = "bandcamp"
    IE_DESC = "Bandcamp.com tracks and albums"
    _VALID_URL = r"^(?:https?://)?(?P<artist>[^.]+)\.bandcamp\.com/(?:track|album)/(?P<id>[^/?#]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        item_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=item_id, fatal=False)

        title = f"Bandcamp Media {item_id}"
        uploader = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        # Parse data-tralbum
        tralbum_match = re.search(r'data-tralbum=["\']({.+?})["\']', webpage)
        if tralbum_match:
            try:
                raw_json = tralbum_match.group(1).replace("&quot;", '"')
                tralbum = json.loads(raw_json)
                trackinfo = tralbum.get("trackinfo", [])
                if trackinfo:
                    first_track = trackinfo[0]
                    title = first_track.get("title", title)
                    duration = first_track.get("duration")
                    file_dict = first_track.get("file", {})
                    for format_name, stream_url in file_dict.items():
                        ext = "mp3" if "mp3" in format_name else "mp3"
                        formats.append(
                            MediaFormat(
                                format_id=format_name,
                                url=stream_url,
                                ext=ext,
                                vcodec="none",
                                acodec=ext,
                                format_note=format_name,
                            )
                        )
                uploader = tralbum.get("artist")
            except Exception:
                pass

        if not formats:
            og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url"], webpage)
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_audio:
                formats.append(MediaFormat(format_id="og-audio", url=og_audio, ext="mp3", vcodec="none", acodec="mp3"))
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            uploader=uploader,
            duration=duration,
            thumbnail=thumbnail,
            formats=formats,
        )
