"""Freesound, Hearthis.at, and Jamendo audio extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class FreesoundIE(InfoExtractor):
    IE_NAME = "freesound"
    IE_DESC = "Freesound, Hearthis.at, and Jamendo music and audio extractor"
    _VALID_URL = r"https?://(?:(?:www\.)?freesound\.org/people/[^/]+/sounds/(?P<id>\d+)|(?:www\.)?hearthis\.at/(?P<hearthis_user>[^/]+)/(?P<hearthis_id>[^/?#&]+)|(?:www\.)?jamendo\.com/track/(?P<jamendo_id>\d+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        audio_id = m.group("id") or m.group("hearthis_id") or m.group("jamendo_id") or "audio"
        webpage = self._download_webpage(url, video_id=audio_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Audio Track {audio_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find direct mp3 or flac or ogg links
        for m_audio in re.finditer(r'["\'](https?://[^"\']+\.(?:mp3|flac|wav|ogg|m4a|m3u8)[^"\']*)["\']', webpage):
            src = m_audio.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=audio_id, fatal=False))
            elif not any(f.url == src for f in formats):
                ext = "mp3" if ".mp3" in src else ("flac" if ".flac" in src else ("ogg" if ".ogg" in src else "mp3"))
                formats.append(MediaFormat(format_id=f"audio-{ext}-{len(formats)}", url=src, ext=ext, vcodec="none"))

        return MediaInfo(
            id=audio_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
