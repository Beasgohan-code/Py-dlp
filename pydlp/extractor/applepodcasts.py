"""Apple Podcasts and Apple Music extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class ApplePodcastsIE(InfoExtractor):
    IE_NAME = "applepodcasts"
    IE_DESC = "Apple Podcasts and Apple Music media extractor"
    _VALID_URL = r"https?://(?:podcasts|music)\.apple\.com/(?:[a-z]{2}/)?(?:podcast/[^/]+/id\d+\?i=(?P<ep_id>\d+)|podcast/(?:[^/]+/)?id(?P<id>\d+)|album/[^/]+/(?P<album_id>\d+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        media_id = m.group("ep_id") or m.group("id") or m.group("album_id") or "podcast"
        webpage = self._download_webpage(url, video_id=media_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Apple Podcast {media_id}")
        title = re.sub(r"\s*on Apple Podcasts\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Look for schema.org audio or enclosure audio links
        for m_audio in re.finditer(r'["\'](https?://[^"\']+\.(?:mp3|m4a|aac|wav|ogg|m3u8)[^"\']*)["\']', webpage):
            audio_url = m_audio.group(1)
            if "mzstatic.com" in audio_url or "podcast" in audio_url or "feeds" in audio_url or ".mp3" in audio_url:
                if ".m3u8" in audio_url:
                    formats.extend(self._extract_m3u8_formats(audio_url, video_id=media_id, fatal=False))
                else:
                    ext = "mp3" if ".mp3" in audio_url else ("m4a" if ".m4a" in audio_url else "mp3")
                    formats.append(
                        MediaFormat(
                            format_id=f"audio-{ext}-{len(formats)}",
                            url=audio_url,
                            ext=ext,
                            vcodec="none",
                            acodec="mp3" if ext == "mp3" else "aac",
                        )
                    )

        return MediaInfo(
            id=media_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
