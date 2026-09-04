"""Mixdrop video extractor."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class MixdropIE(InfoExtractor):
    """Extractor for Mixdrop videos."""

    IE_NAME = "mixdrop"
    IE_DESC = "Mixdrop.co and mirror video hosts"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:mixdrop\.(?:co|to|sx|bz|ch|to)|mixdroop\.(?:com|co))/(?:f|e)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        embed_url = f"https://mixdrop.co/e/{video_id}"
        webpage = self._download_webpage(embed_url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"Mixdrop Video {video_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Look for MDCore.wurl = "//.../..." or eval unpacker
            wurl_match = re.search(r'MDCore\.wurl\s*=\s*["\']([^"\']+)["\']', webpage)
            if wurl_match:
                wurl = wurl_match.group(1)
                full_wurl = f"https:{wurl}" if wurl.startswith("//") else wurl
                formats.append(
                    MediaFormat(
                        format_id="mixdrop-mp4",
                        url=full_wurl,
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
