"""YouJizz media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class YouJizzIE(InfoExtractor):
    IE_NAME = "youjizz"
    IE_DESC = "YouJizz video extractor"
    _VALID_URL = r"https?://(?:www\.)?youjizz\.com/videos/[^/?#]+-(?P<id>\d+)\.html"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_regex(
            [r'<title>([^<]+)</title>', r'<h1[^>]*>([^<]+)</h1>'],
            webpage,
            "title",
            default=f"YouJizz Video {video_id}",
        )
        title = re.sub(r"\s*-\s*YouJizz\.com\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        uploader = self._html_search_regex(
            r'class="uploader-name"[^>]*>([^<]+)', webpage, "uploader", default=None
        )

        formats: List[MediaFormat] = []

        # JSON encodings or video sources
        for m in re.finditer(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
            video_url = m.group(1)
            if "youjizz" in video_url or "cdn" in video_url or "media" in video_url:
                res_match = re.search(r'(\d+)p', video_url)
                height = int(res_match.group(1)) if res_match else None
                formats.append(
                    MediaFormat(
                        format_id=f"http-{height}p" if height else f"http-{len(formats)}",
                        url=video_url,
                        ext="mp4",
                        height=height,
                    )
                )

        hls_match = re.search(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
        if hls_match:
            formats.extend(self._extract_m3u8_formats(hls_match.group(1), video_id=video_id, fatal=False))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            uploader=uploader,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
