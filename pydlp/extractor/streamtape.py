"""Streamtape video extractor."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class StreamtapeIE(InfoExtractor):
    """Extractor for Streamtape videos."""

    IE_NAME = "streamtape"
    IE_DESC = "Streamtape.com and mirror video hosts"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:streamtape\.(?:com|to|net|xyz|site)|strtape\.(?:tech|cloud))/(?:v|e)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        embed_url = f"https://streamtape.com/e/{video_id}"
        webpage = self._download_webpage(embed_url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Streamtape Video {video_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Streamtape robot link deobfuscation
            # document.getElementById('robotlink').innerHTML = '//streamtape.com/get_video?id=...' + ('&token=...');
            robot_match = re.search(
                r"document\.getElementById\(['\"]robotlink['\"]\)\.innerHTML\s*=\s*['\"]([^'\"]+)['\"]\s*\+\s*\(['\"]([^'\"]+)['\"]\)\.substring\(\d+\)",
                webpage,
            ) or re.search(
                r"document\.getElementById\(['\"]robotlink['\"]\)\.innerHTML\s*=\s*['\"]([^'\"]+)['\"]\s*\+\s*['\"]([^'\"]+)['\"]",
                webpage,
            )
            if robot_match:
                p1, p2 = robot_match.groups()
                direct_url = f"https:{p1}{p2}" if p1.startswith("//") else f"https://{p1}{p2}"
                formats.append(
                    MediaFormat(
                        format_id="streamtape-hd",
                        url=direct_url,
                        ext="mp4",
                        http_headers={"Referer": embed_url},
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=embed_url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=embed_url,
            thumbnail=thumbnail,
            formats=formats,
        )
