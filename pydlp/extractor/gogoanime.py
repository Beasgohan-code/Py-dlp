"""Gogoanime and Anitaku anime extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, urljoin
from pydlp.extractor.base import InfoExtractor


class GogoAnimeIE(InfoExtractor):
    """Extractor for Gogoanime and Anitaku anime episodes."""

    IE_NAME = "gogoanime"
    IE_DESC = "Gogoanime and Anitaku anime stream extractor"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:gogoanime3?\.(?:co|to|cl|io|film)|anitaku\.(?:to|so|bz)|gogoanimes\.(?:fi|to))/(?:category/)?(?P<id>[a-zA-Z0-9-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        item_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=item_id, fatal=False)

        title = f"Gogoanime {item_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

            # Look for iframe servers: vidstreaming, streamwish, doodstream, mp4upload
            iframe_matches = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', webpage, re.IGNORECASE)
            for iframe_src in iframe_matches:
                full_src = urljoin(url, iframe_src)
                if full_src.startswith("//"):
                    full_src = f"https:{full_src}"

                # Query embed webpage
                embed_html = self._download_webpage(full_src, video_id=item_id, headers={"Referer": url}, fatal=False)
                if embed_html:
                    # Look for m3u8 playlist URLs
                    m3u8_matches = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', embed_html)
                    for m_url in m3u8_matches:
                        formats.extend(self._extract_m3u8_formats(m_url, item_id, headers={"Referer": full_src}))

                    # Look for progressive mp4 files
                    mp4_matches = re.findall(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', embed_html)
                    for p_url in mp4_matches:
                        formats.append(
                            MediaFormat(
                                format_id=f"http-{len(formats)}",
                                url=p_url,
                                ext="mp4",
                                http_headers={"Referer": full_src},
                            )
                        )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            formats=formats,
        )
