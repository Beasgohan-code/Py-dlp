"""Mastodon, Misskey, and Fediverse microblogging video extractor."""

from __future__ import annotations

import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class MastodonIE(InfoExtractor):
    IE_NAME = "mastodon"
    IE_DESC = "Mastodon, Misskey, and Fediverse video posts extractor"
    _VALID_URL = r"https?://[^/]+/@(?P<user>[^/]+)/(?P<id>\d+|[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        user = m.group("user") if m else "user"
        status_id = m.group("id") if m else "status"
        full_id = f"{user}_{status_id}"

        webpage = self._download_webpage(url, video_id=full_id)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Post by {user}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        for m_src in re.finditer(r'["\'](https?://[^"\']*(?:media_attachments|files|system)[^"\']+\.(?:mp4|webm|m3u8|mp3))["\']', webpage):
            src = m_src.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=full_id, fatal=False))
            elif not any(f.url == src for f in formats):
                ext = "mp4" if ".mp4" in src else ("webm" if ".webm" in src else "mp3")
                formats.append(MediaFormat(format_id=f"fediverse-{ext}-{len(formats)}", url=src, ext=ext))

        return MediaInfo(
            id=full_id,
            title=title,
            webpage_url=url,
            uploader=user,
            description=description,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
