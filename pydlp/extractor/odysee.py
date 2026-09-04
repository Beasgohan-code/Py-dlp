"""Odysee and LBRY media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class OdyseeIE(InfoExtractor):
    IE_NAME = "odysee"
    IE_DESC = "Odysee.com and LBRY.tv video extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:odysee\.com|lbry\.tv)/(?:@[^/]+/)?(?P<id>[^/?#&:]+)(?::[a-zA-Z0-9]+)?"

    def _real_extract(self, url: str) -> MediaInfo:
        claim_name = self._match_id(url)
        webpage = self._download_webpage(url, video_id=claim_name)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Odysee {claim_name}")
        title = re.sub(r"\s*on Odysee\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find streaming URL or HLS / MP4
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=claim_name, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        # Fallback to direct player source
        video_src = self._search_regex(
            r'<video[^>]+src=["\'](https?://[^"\']+)["\']',
            webpage,
            "video_src",
            default=None,
        )
        if video_src and not any(f.url == video_src for f in formats):
            formats.append(MediaFormat(format_id="http-direct", url=video_src, ext="mp4"))

        return MediaInfo(
            id=claim_name,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
