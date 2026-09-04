"""TED talks extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class TedIE(InfoExtractor):
    IE_NAME = "ted"
    IE_DESC = "TED.com talks and presentations extractor"
    _VALID_URL = r"https?://(?:www\.)?ted\.com/talks/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        talk_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=talk_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"TED Talk {talk_id}")
        title = re.sub(r"\s*\|\s*TED\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find __NEXT_DATA__ or JSON state
        next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', webpage)
        if next_data:
            try:
                data = json.loads(next_data.group(1))
                props = data.get("props", {}).get("pageProps", {})
                video_data = props.get("videoData", {}) or props.get("talk", {})
                hls_url = video_data.get("playerData", {}).get("resources", {}).get("hls", {}).get("stream")
                if hls_url:
                    formats.extend(self._extract_m3u8_formats(hls_url, video_id=talk_id, fatal=False))
            except Exception:
                pass

        # Regex fallback
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src and "ted" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=talk_id, fatal=False))
            elif ".mp4" in src and "ted" in src:
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=talk_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
