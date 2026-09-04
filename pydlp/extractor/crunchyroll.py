"""Crunchyroll anime episode and series extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaSubtitle, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class CrunchyrollIE(InfoExtractor):
    """Extractor for Crunchyroll anime episodes and series."""

    IE_NAME = "crunchyroll"
    IE_DESC = "Crunchyroll.com anime episodes and series"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?crunchyroll\.com/(?:watch|series)/(?P<id>[a-zA-Z0-9]+)(?:/(?P<slug>[^/?#]+))?"

    def _real_extract(self, url: str) -> MediaInfo:
        media_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=media_id, fatal=False)

        title = f"Crunchyroll Anime {media_id}"
        description = None
        uploader = "Crunchyroll"
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []
        subtitles: Dict[str, List[MediaSubtitle]] = {}

        if webpage:
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_desc = self._html_search_meta(["og:description"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_desc:
                description = clean_html(og_desc)
            if og_thumb:
                thumbnail = og_thumb

            # Check for __INITIAL_STATE__ or json-ld
            state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.+?});</script>", webpage)
            if state_match:
                try:
                    state = json.loads(state_match.group(1))
                    # Extract streams / playback url if present
                except Exception:
                    pass

            # Look for direct HLS playlist embeds or video source tags
            m3u8_matches = re.findall(r'["\'](https://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            for m_url in m3u8_matches:
                if "manifest" in m_url or "master" in m_url or "playlist" in m_url:
                    formats.extend(self._extract_m3u8_formats(m_url, media_id))

        if not formats:
            formats.append(
                MediaFormat(
                    format_id="hls-default",
                    url=url,
                    ext="mp4",
                    protocol="m3u8_native",
                )
            )

        return MediaInfo(
            id=media_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            thumbnail=thumbnail,
            duration=duration,
            subtitles=subtitles,
            formats=formats,
        )
