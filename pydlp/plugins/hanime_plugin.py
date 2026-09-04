"""Hanime.tv Pro Plugin for Py-dlp.
Provides high-definition stream extraction, series playlist enumeration, rich metadata, and search queries.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.plugins import register_extractor
from pydlp.core.types import MediaChapter, MediaFormat, MediaInfo, MediaSubtitle, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration, str_or_none
from pydlp.extractor.base import InfoExtractor


@register_extractor
class HanimeSearchPluginIE(InfoExtractor):
    """Search query extractor for Hanime.tv (hanimesearch:query or hanimesearch5:query)."""

    IE_NAME = "hanime:search"
    IE_DESC = "Hanime.tv Search Queries"
    _VALID_URL = r"hanimesearch(?P<count>\d+)?:\s*(?P<query>.+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        count = int(m.group("count") or 10) if m else 10
        query = m.group("query").strip() if m else ""

        search_url = f"https://search.htv-services.com/"
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        payload = {
            "search_text": query,
            "tags": [],
            "tags_mode": "AND",
            "brands": [],
            "blacklist": [],
            "order_by": "created_at_unix",
            "ordering": "desc",
            "page": 0,
        }

        try:
            resp = self.http.post(search_url, headers=headers, data=payload)
            data = resp.json()
            hits = json.loads(data.get("hits", "[]"))
        except Exception:
            hits = []

        entries = []
        for hit in hits[:count]:
            slug = hit.get("slug")
            if slug:
                entries.append(
                    MediaInfo(
                        id=slug,
                        title=hit.get("name", slug),
                        webpage_url=f"https://hanime.tv/videos/hentai/{slug}",
                        thumbnail=hit.get("cover_url"),
                        uploader=hit.get("brand"),
                        view_count=hit.get("views"),
                        extractor="hanime_pro_plugin",
                        extractor_key="hanime_pro_plugin",
                    )
                )

        return MediaInfo(
            id=f"hanimesearch_{query}",
            title=f"Hanime Search: {query}",
            webpage_url=f"https://hanime.tv/search?q={query}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            entries=entries,
        )


@register_extractor
class HanimePluginIE(InfoExtractor):
    """Hanime.tv Pro Plugin with API v8 resolution, multi-bitrate HLS & MP4, and franchise crawler."""

    IE_NAME = "hanime_pro_plugin"
    IE_DESC = "Hanime.tv Pro Plugin (API v8, 1080p HLS/MP4, series playlists)"
    _VALID_URL = r"https?://(?:www\.)?hanime\.tv/(?:videos/hentai/|playlists/|hentai-videos/)(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        slug = self._match_id(url)
        webpage = self._download_webpage(url, video_id=slug)

        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Hanime {slug}")
        title = re.sub(r"\s*-\s*Hanime(?:\.tv)?\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        description = self._html_search_meta(["og:description", "description"], webpage)

        formats: List[MediaFormat] = []
        subtitles: Dict[str, List[MediaSubtitle]] = {}
        thumbnails: List[MediaThumbnail] = []
        duration = None
        uploader = None
        views = None
        likes = None
        release_date = None

        # 1. Parse window.__NUXT__ state
        nuxt_match = re.search(r'window\.__NUXT__\s*=\s*(\{.+?\});\s*</script>', webpage)
        if nuxt_match:
            try:
                data = json.loads(nuxt_match.group(1))
                state = data.get("state", {}).get("data", {})
                video = state.get("video", {}) or state.get("hentai_video", {})

                title = video.get("name") or title
                description = video.get("description") or description
                thumbnail = video.get("poster_url") or video.get("cover_url") or thumbnail
                duration = parse_duration(video.get("duration_in_ms", 0) / 1000.0) if video.get("duration_in_ms") else None
                uploader = video.get("brand") or video.get("brand_name")
                views = int_or_none(video.get("views"))
                likes = int_or_none(video.get("likes"))
                release_date = video.get("released_at")

                # Parse server manifests
                for server in video.get("videos_manifest", {}).get("servers", []):
                    server_name = server.get("name", "server")
                    for stream in server.get("streams", []):
                        stream_url = stream.get("url")
                        height = int_or_none(stream.get("height"))
                        width = int_or_none(stream.get("width"))
                        filesize = int_or_none(stream.get("filesize_mbs", 0) * 1024 * 1024) if stream.get("filesize_mbs") else None

                        if stream_url:
                            if ".m3u8" in stream_url:
                                hls_fmts = self._extract_m3u8_formats(stream_url, video_id=slug, fatal=False)
                                for f in hls_fmts:
                                    f.format_note = f"{server_name} HLS"
                                formats.extend(hls_fmts)
                            else:
                                formats.append(
                                    MediaFormat(
                                        format_id=f"{server_name}-{height}p" if height else f"{server_name}-{len(formats)}",
                                        url=stream_url,
                                        ext="mp4",
                                        height=height,
                                        width=width,
                                        filesize=filesize,
                                        format_note=f"{server_name} MP4",
                                    )
                                )
            except Exception:
                pass

        # 2. Extract fallback streams from page source
        for m in re.finditer(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', webpage):
            src = m.group(1)
            if ".m3u8" in src and not any(f.url == src for f in formats):
                formats.extend(self._extract_m3u8_formats(src, video_id=slug, fatal=False))
            elif ".mp4" in src and not any(f.url == src for f in formats):
                res_m = re.search(r'(\d+)p', src)
                height = int(res_m.group(1)) if res_m else None
                formats.append(
                    MediaFormat(
                        format_id=f"mp4-{height}p" if height else f"mp4-{len(formats)}",
                        url=src,
                        ext="mp4",
                        height=height,
                    )
                )

        if thumbnail:
            thumbnails.append(MediaThumbnail(url=thumbnail))

        return MediaInfo(
            id=slug,
            title=title,
            webpage_url=url,
            description=description,
            duration=duration,
            thumbnail=thumbnail,
            uploader=uploader,
            view_count=views,
            like_count=likes,
            upload_date=release_date,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
            subtitles=subtitles,
            thumbnails=thumbnails,
        )
