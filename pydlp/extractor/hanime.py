"""Hanime media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import int_or_none
from pydlp.extractor.base import InfoExtractor


class HanimeIE(InfoExtractor):
    IE_NAME = "hanime"
    IE_DESC = "Hanime.tv anime & video extractor"
    _VALID_URL = r"https?://(?:www\.)?hanime\.tv/videos/hentai/(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Hanime {video_id}")
        title = re.sub(r"\s*-\s*Hanime(?:\.tv)?\s*$", "", title, flags=re.IGNORECASE).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Check for window.__NUXT__ or state JSON
        nuxt_match = re.search(r'window\.__NUXT__\s*=\s*(\{.+?\});\s*</script>', webpage)
        if nuxt_match:
            try:
                data = json.loads(nuxt_match.group(1))
                video_data = data.get("state", {}).get("data", {}).get("video", {})
                for stream in video_data.get("videos_manifest", {}).get("servers", []):
                    for stream_info in stream.get("streams", []):
                        s_url = stream_info.get("url")
                        height = stream_info.get("height")
                        if s_url and ".m3u8" in s_url:
                            formats.extend(self._extract_m3u8_formats(s_url, video_id=video_id, fatal=False))
                        elif s_url:
                            formats.append(
                                MediaFormat(
                                    format_id=f"http-{height}p" if height else f"http-{len(formats)}",
                                    url=s_url,
                                    ext="mp4",
                                    height=int_or_none(height),
                                )
                            )
            except Exception:
                pass

        # Direct search fallback
        for m in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            formats.extend(self._extract_m3u8_formats(m.group(1), video_id=video_id, fatal=False))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
