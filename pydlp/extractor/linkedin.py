"""LinkedIn media extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class LinkedInIE(InfoExtractor):
    IE_NAME = "linkedin"
    IE_DESC = "LinkedIn posts and video extractor"
    _VALID_URL = r"https?://(?:www\.)?linkedin\.com/(?:posts/[^/?#&]+|feed/update/urn:li:activity:(?P<activity_id>\d+)|learning/[^/]+/(?P<learning_id>[^/?#&]+)|learning-login/[^?#]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        media_id = (m.group("activity_id") if m and "activity_id" in m.groupdict() else None) or "post"
        webpage = self._download_webpage(url, video_id=media_id)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default="LinkedIn Video Post")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []

        # Find progressive mp4 and HLS streams
        for m in re.finditer(r'data-sources=["\'](\[.+?\])["\']', webpage):
            try:
                import json
                sources = json.loads(m.group(1).replace("&quot;", '"'))
                for s in sources:
                    if isinstance(s, dict) and s.get("src"):
                        formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=s["src"], ext="mp4"))
            except Exception:
                pass

        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m.group(1)
            if "dms.licdn.com" in src or "linkedin" in src:
                if ".m3u8" in src:
                    formats.extend(self._extract_m3u8_formats(src, video_id=media_id, fatal=False))
                elif ".mp4" in src and not any(f.url == src for f in formats):
                    formats.append(MediaFormat(format_id=f"mp4-{len(formats)}", url=src, ext="mp4"))

        return MediaInfo(
            id=media_id,
            title=title,
            webpage_url=url,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
