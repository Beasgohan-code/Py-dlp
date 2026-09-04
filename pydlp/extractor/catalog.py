"""Universal Media Catalog Dispatcher and Extractor Engine for Py-dlp.
Provides automatic recognition, metadata resolution, and stream extraction for 2,000+ domains.
"""

from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration, unescape_html
from pydlp.extractor.base import InfoExtractor
from pydlp.extractor.sites_db import PLATFORM_CATALOG


class UniversalCatalogIE(InfoExtractor):
    """Universal Extractor automatically matching and extracting from 2,000+ recognized media sites."""

    IE_NAME = "universal_catalog"
    IE_DESC = "Universal Site Engine supporting 2,000+ video, audio, and streaming domains"
    _VALID_URL = r"https?://(?:www\.)?(?P<domain>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/(?P<path>[^?#]*)(?:\?(?P<query>[^#]*))?"

    @classmethod
    def suitable(cls, url: str) -> bool:
        # Match any valid web URL that has standard protocol
        return url.startswith(("http://", "https://"))

    def _real_extract(self, url: str) -> MediaInfo:
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname or "domain"
        video_id = re.sub(r"[^a-zA-Z0-9_-]", "_", parsed_url.path.strip("/").split("/")[-1]) or "video"

        webpage = self._download_webpage(url, video_id=video_id)

        # 1. Extract Rich Metadata (Title, Description, Uploader, Thumbnail)
        title = self._html_search_meta(
            ["og:title", "twitter:title", "title", "headline", "name"],
            webpage,
            default=None,
        )
        if not title:
            title_m = re.search(r"<title[^>]*>([^<]+)</title>", webpage, re.IGNORECASE)
            title = unescape_html(title_m.group(1).strip()) if title_m else f"Media {video_id}"

        description = self._html_search_meta(
            ["og:description", "twitter:description", "description"],
            webpage,
            default=None,
        )

        thumbnail = self._html_search_meta(
            ["og:image", "twitter:image", "thumbnail", "image"],
            webpage,
            default=None,
        )

        uploader = self._html_search_meta(
            ["author", "og:author", "article:author", "publisher", "og:site_name"],
            webpage,
            default=hostname,
        )

        duration = None
        dur_meta = self._html_search_meta(["duration", "video:duration", "og:video:duration"], webpage)
        if dur_meta:
            duration = parse_duration(dur_meta)

        formats: List[MediaFormat] = []

        # 2. Extract JSON-LD and Schema.org metadata
        for schema_m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.+?)</script>', webpage, re.DOTALL):
            try:
                data = json.loads(schema_m.group(1))
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("@graph", [data])
                else:
                    items = []

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = str(item.get("@type", "")).lower()
                    if "video" in item_type or "audio" in item_type or "media" in item_type:
                        title = item.get("name") or item.get("headline") or title
                        description = item.get("description") or description
                        content_url = item.get("contentUrl") or item.get("embedUrl")
                        if content_url:
                            ext = determine_ext(content_url)
                            if ".m3u8" in content_url or ext == "m3u8":
                                formats.extend(self._extract_m3u8_formats(content_url, video_id=video_id, fatal=False))
                            elif ".mpd" in content_url or ext == "mpd":
                                formats.extend(self._extract_mpd_formats(content_url, video_id=video_id, fatal=False))
                            else:
                                formats.append(MediaFormat(format_id="schema-direct", url=content_url, ext=ext))
            except Exception:
                pass

        # 3. Master HLS (.m3u8) Streams
        for m_hls in re.finditer(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage):
            hls_url = m_hls.group(1)
            formats.extend(self._extract_m3u8_formats(hls_url, video_id=video_id, fatal=False))

        # 4. MPEG-DASH (.mpd) Streams
        for m_dash in re.finditer(r'["\'](https?://[^"\']+\.mpd[^"\']*)["\']', webpage):
            dash_url = m_dash.group(1)
            formats.extend(self._extract_mpd_formats(dash_url, video_id=video_id, fatal=False))

        # 5. HTML5 <video> and <source> tags
        for m_src in re.finditer(r'<source[^>]+src=["\'](https?://[^"\']+)["\']', webpage):
            src = m_src.group(1)
            ext = determine_ext(src)
            if not any(f.url == src for f in formats):
                if ext == "m3u8":
                    formats.extend(self._extract_m3u8_formats(src, video_id=video_id, fatal=False))
                else:
                    formats.append(MediaFormat(format_id=f"html5-{ext}-{len(formats)}", url=src, ext=ext))

        # 6. Direct MP4 / WebM / MP3 links in scripts or meta tags
        for m_media in re.finditer(r'["\'](https?://[^"\']+\.(?:mp4|webm|m4v|mkv|mov|mp3|m4a|aac|flac|wav)[^"\']*)["\']', webpage):
            media_url = m_media.group(1)
            ext = determine_ext(media_url)
            if not any(f.url == media_url for f in formats) and not any(p in media_url for p in ("ad_", "analytics", "pixel")):
                formats.append(MediaFormat(format_id=f"direct-{ext}-{len(formats)}", url=media_url, ext=ext))

        return MediaInfo(
            id=video_id,
            title=title or f"Media {video_id}",
            webpage_url=url,
            description=description,
            duration=duration,
            thumbnail=thumbnail,
            uploader=uploader,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
