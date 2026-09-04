"""XVideos and XNXX video extractor."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import urllib.parse

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, unescape_html
from pydlp.extractor.base import InfoExtractor


class XVideosIE(InfoExtractor):
    """Extractor for XVideos and XNXX videos."""

    IE_NAME = "xvideos"
    IE_DESC = "XVideos.com and XNXX.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|[a-z]{2}\.)?(?:xvideos\.com/video(?P<id>\d+)|xnxx\.com/video-(?P<xnxx_id>[a-zA-Z0-9]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("xnxx_id")
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"XVideos {video_id}"
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
            dur_str = self._html_search_meta(["video:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if dur_str:
                duration = parse_duration(dur_str)

            # html5player functions in javascript
            # setUrlHigh('...'), setUrlLow('...'), setUrlHLS('...')
            hls_match = re.search(r"html5player\.setVideoHLS\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", webpage) or re.search(r"setVideoHLS\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", webpage)
            if hls_match:
                hls_url = hls_match.group(1)
                formats.extend(self._extract_m3u8_formats(hls_url, video_id))

            high_match = re.search(r"html5player\.setVideoUrlHigh\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", webpage)
            if high_match:
                formats.append(
                    MediaFormat(
                        format_id="http-high",
                        url=high_match.group(1),
                        ext="mp4",
                        format_note="High Quality",
                    )
                )

            low_match = re.search(r"html5player\.setVideoUrlLow\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", webpage)
            if low_match:
                formats.append(
                    MediaFormat(
                        format_id="http-low",
                        url=low_match.group(1),
                        ext="mp4",
                        format_note="Low Quality",
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            duration=duration,
            age_limit=18,
            formats=formats,
        )
