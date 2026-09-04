"""DTube media extractor."""

from __future__ import annotations

import json
import re
from typing import List

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class DTubeIE(InfoExtractor):
    IE_NAME = "dtube"
    IE_DESC = "DTube decentralized video extractor"
    _VALID_URL = r"https?://(?:www\.)?d\.tube/#!/v/(?P<user>[^/]+)/(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        user = m.group("user") if m else "user"
        video_id = m.group("id") if m else "id"
        full_id = f"{user}_{video_id}"

        webpage = self._download_webpage(url, video_id=full_id)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"DTube {video_id}")
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)

        formats: List[MediaFormat] = []

        # IPFS direct hash resolution or gateway links
        for m_ipfs in re.finditer(r'["\'](https?://[^"\']*(?:ipfs|gateway)[^"\']+\.(?:mp4|m3u8)[^"\']*)["\']', webpage):
            src = m_ipfs.group(1)
            if ".m3u8" in src:
                formats.extend(self._extract_m3u8_formats(src, video_id=full_id, fatal=False))
            elif ".mp4" in src:
                formats.append(MediaFormat(format_id=f"ipfs-mp4-{len(formats)}", url=src, ext="mp4"))

        # Fallback IPFS format if direct hash is found
        ipfs_hash = self._search_regex(r'["\'](?:videoHash|ipfsHash)["\']\s*:\s*["\']([a-zA-Z0-9]+)["\']', webpage, "ipfs_hash", default=None)
        if ipfs_hash:
            formats.append(
                MediaFormat(
                    format_id="ipfs-gateway",
                    url=f"https://ipfs.io/ipfs/{ipfs_hash}",
                    ext="mp4",
                    format_note="IPFS Gateway",
                )
            )

        return MediaInfo(
            id=full_id,
            title=title,
            webpage_url=url,
            uploader=user,
            thumbnail=thumbnail,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
