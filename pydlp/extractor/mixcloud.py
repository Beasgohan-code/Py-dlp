"""Mixcloud DJ sets and radio show extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class MixcloudIE(InfoExtractor):
    """Extractor for Mixcloud radio shows and DJ sets."""

    IE_NAME = "mixcloud"
    IE_DESC = "Mixcloud.com DJ sets and audio podcasts"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?mixcloud\.com/(?P<user>[^/]+)/(?P<id>[^/?#]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        user = m.group("user")
        slug = m.group("id")

        webpage = self._download_webpage(url, video_id=slug, fatal=False)
        title = f"Mixcloud Cloudcast {slug}"
        uploader = user
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            dur_str = self._html_search_meta(["music:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if dur_str:
                duration = parse_duration(dur_str)

            # Check for m-play-info or stream URLs
            stream_matches = re.findall(r'["\'](https?://[^"\']+\.(?:m3u8|m4a|mp3)[^"\']*)["\']', webpage)
            for s_url in stream_matches:
                if ".m3u8" in s_url:
                    formats.extend(self._extract_m3u8_formats(s_url, slug, ext="m4a"))
                else:
                    formats.append(
                        MediaFormat(
                            format_id=f"audio-{len(formats)}",
                            url=s_url,
                            ext="m4a",
                            vcodec="none",
                            acodec="aac",
                        )
                    )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="m4a", vcodec="none", acodec="aac"))

        return MediaInfo(
            id=slug,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            uploader=uploader,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
