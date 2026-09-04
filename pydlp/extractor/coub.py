"""Coub media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class CoubIE(InfoExtractor):
    IE_NAME = "coub"
    IE_DESC = "Coub.com looped video extractor"
    _VALID_URL = r"https?://(?:www\.)?coub\.com/view/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        coub_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=coub_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Coub {coub_id}")
        title = re.sub(r"\s*-\s*Coub\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find coub video streams or audio/video JSON
        coub_json = re.search(r'<script id="coubPageCoubJson" type="text/json">(.+?)</script>', webpage)
        if coub_json:
            try:
                data = json.loads(coub_json.group(1))
                file_versions = data.get("file_versions", {})
                html5 = file_versions.get("html5", {})
                for v_res, v_info in html5.get("video", {}).items():
                    if isinstance(v_info, dict) and v_info.get("url"):
                        formats.append(MediaFormat(format_id=f"video-{v_res}", url=v_info["url"], ext="mp4"))
                for a_res, a_info in html5.get("audio", {}).items():
                    if isinstance(a_info, dict) and a_info.get("url"):
                        formats.append(MediaFormat(format_id=f"audio-{a_res}", url=a_info["url"], ext="mp3", vcodec="none"))
            except Exception:
                pass

        if not formats:
            for m in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|mp3|m3u8)[^"\']*)["\']', webpage):
                src = m.group(1)
                if ".m3u8" in src:
                    formats.extend(self._extract_m3u8_formats(src, video_id=coub_id, fatal=False))
                elif ".mp4" in src and not any(f.url == src for f in formats):
                    formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=coub_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
