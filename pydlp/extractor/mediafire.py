"""MediaFire and Mega direct file host extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class MediaFireIE(InfoExtractor):
    IE_NAME = "mediafire"
    IE_DESC = "MediaFire and Mega cloud storage media extractor"
    _VALID_URL = r"https?://(?:www\.)?(?:mediafire\.com/(?:file|download)/(?P<id>[a-zA-Z0-9]+)|mega\.(?:nz|co\.nz)/(?:file/|#!)(?P<mega_id>[a-zA-Z0-9_-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        file_id = m.group("id") or m.group("mega_id") or "file"
        webpage = self._download_webpage(url, video_id=file_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Media File {file_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # Find direct download link
        direct_link = self._search_regex(
            [r'aria-label="Download file"[^>]+href=["\'](https?://download\d*\.mediafire\.com/[^"\']+)["\']',
             r'href=["\'](https?://download\d*\.mediafire\.com/[^"\']+)["\']'],
            webpage,
            "direct_link",
            default=None,
        )

        if direct_link:
            formats.append(MediaFormat(format_id="direct", url=direct_link, ext="mp4"))

        for m_src in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m4v|mkv|mp3|m4a|zip|rar)[^"\']*)["\']', webpage):
            src = m_src.group(1)
            if not any(f.url == src for f in formats) and ("mediafire.com" in src or "mega." in src):
                formats.append(MediaFormat(format_id=f"file-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=file_id,
            title=title,
            webpage_url=url,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
