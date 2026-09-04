"""BitChute media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class BitChuteIE(InfoExtractor):
    IE_NAME = "bitchute"
    IE_DESC = "BitChute.com video extractor"
    _VALID_URL = r"https?://(?:www\.)?bitchute\.com/video/(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"BitChute Video {video_id}")
        title = re.sub(r"\s*-\s*BitChute\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)
        uploader = self._html_search_regex(
            [r'class="owner"[^>]*><a[^>]*>([^<]+)</a>', r'<p class="name"><a[^>]*>([^<]+)</a>'],
            webpage,
            "uploader",
            default=None,
        )

        formats: List[MediaFormat] = []

        # Find direct mp4 seed links
        for m in re.finditer(r'<source[^>]+src=["\'](https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
            formats.append(MediaFormat(format_id="mp4-direct", url=m.group(1), ext="mp4"))

        if not formats:
            for m in re.finditer(r'["\'](https?://seed\d*\.bitchute\.com/[^"\']+\.mp4[^"\']*)["\']', webpage):
                formats.append(MediaFormat(format_id="seed-mp4", url=m.group(1), ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            uploader=uploader,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
