"""Medal.tv gaming clips extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class MedalTVIE(InfoExtractor):
    IE_NAME = "medaltv"
    IE_DESC = "Medal.tv gaming clips and highlights extractor"
    _VALID_URL = r"https?://(?:www\.)?medal\.tv/games/[^/]+/clips/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        clip_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=clip_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Medal Clip {clip_id}")
        title = re.sub(r"\s*-\s*Medal\.tv\s*$", "", title).strip()
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        for m in re.finditer(r'["\'](https?://[^"\']*(?:medal\.tv|cdn\.medal)[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=clip_id, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=clip_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
