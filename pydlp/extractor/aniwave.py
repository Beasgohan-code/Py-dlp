"""Aniwave, 9anime, HiAnime, and Zoro anime extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, urljoin
from pydlp.extractor.base import InfoExtractor


class AniwaveIE(InfoExtractor):
    """Extractor for 9anime, Aniwave, Zoro, Aniwatch, and HiAnime."""

    IE_NAME = "aniwave"
    IE_DESC = "Aniwave / 9anime / Zoro / HiAnime stream extractor"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:aniwave\.(?:to|lv|vc)|9anime\.(?:to|id|pl)|hianime\.(?:to|nz)|aniwatch\.(?:to|se)|zoro\.(?:to|vc))/(?:watch/)?(?P<id>[a-zA-Z0-9-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        item_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=item_id, fatal=False)

        title = f"Anime Stream {item_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Scan for embedded video player sources
            player_sources = re.findall(r'data-src=["\']([^"\']+)["\']', webpage) + re.findall(
                r'src=["\'](https?://[^"\']*(?:megacloud|vidstream|streamtape|mp4upload|dood)[^"\']*)["\']',
                webpage,
            )
            for src in player_sources:
                full_src = urljoin(url, src)
                formats.append(
                    MediaFormat(
                        format_id=f"embed-{len(formats)}",
                        url=full_src,
                        ext="mp4",
                        http_headers={"Referer": url},
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="play", url=url, ext="mp4"))

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            formats=formats,
        )
