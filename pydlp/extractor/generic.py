"""Generic & Direct Media Extractor."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import List, Optional
import urllib.parse

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration, urljoin
from pydlp.extractor.base import InfoExtractor

_DIRECT_EXT_RE = re.compile(
    r"\.(mp4|m4v|mkv|webm|flv|avi|mov|ts|m3u8|mpd|mp3|m4a|aac|ogg|opus|flac|wav)(\?.*)?$",
    re.IGNORECASE,
)


class GenericIE(InfoExtractor):
    """Fallback extractor for generic websites, HTML5 media, OpenGraph, JSON-LD, and direct files."""

    IE_NAME = "generic"
    IE_DESC = "Generic Webpage & Direct Stream Extractor"
    _VALID_URL = r".+"

    def _real_extract(self, url: str) -> MediaInfo:
        # Check if direct media file link
        path = urllib.parse.urlparse(url).path
        ext = determine_ext(url)
        stem = os.path.splitext(os.path.basename(path))[0] or "media"
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]

        if _DIRECT_EXT_RE.search(url):
            is_audio = ext in ("mp3", "m4a", "aac", "ogg", "opus", "flac", "wav")
            is_hls = ext == "m3u8"
            is_dash = ext == "mpd"

            fmt = MediaFormat(
                format_id="direct",
                url=url,
                ext=ext if not (is_hls or is_dash) else "mp4",
                vcodec="none" if is_audio else None,
                acodec=ext if is_audio else None,
                protocol="m3u8_native" if is_hls else ("dash" if is_dash else "https"),
            )
            return MediaInfo(
                id=stem or url_hash,
                title=stem or f"Direct Media [{url_hash}]",
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=url,
                url=url,
                ext=ext,
                formats=[fmt],
            )

        # Download webpage
        html_doc = self._download_webpage(url, video_id=stem, fatal=False)
        if not html_doc:
            # Fallback direct
            return MediaInfo(
                id=url_hash,
                title=f"Direct Media [{url_hash}]",
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=url,
                url=url,
                formats=[MediaFormat(format_id="http-0", url=url, ext=ext)],
            )

        # Title
        title = (
            self._html_search_meta(["og:title", "twitter:title"], html_doc)
            or self._html_search_regex(r"<title>([^<]+)</title>", html_doc, "title", default=None)
            or stem
        )
        title = clean_html(title)

        # Description
        description = self._html_search_meta(
            ["og:description", "twitter:description", "description"], html_doc
        )

        # Thumbnail
        thumb_url = self._html_search_meta(["og:image", "twitter:image"], html_doc)
        thumbnails = [MediaThumbnail(url=urljoin(url, thumb_url))] if thumb_url else []

        # Duration
        duration_str = self._html_search_meta(["video:duration", "music:duration"], html_doc)
        duration = parse_duration(duration_str)

        formats: List[MediaFormat] = []

        # 1. JSON-LD extraction
        json_ld_matches = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html_doc,
            re.DOTALL | re.IGNORECASE,
        )
        for jld in json_ld_matches:
            try:
                data = json.loads(jld)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    itype = str(item.get("@type", ""))
                    if itype in ("VideoObject", "AudioObject", "MediaObject"):
                        title = item.get("name") or title
                        description = item.get("description") or description
                        content_url = item.get("contentUrl") or item.get("embedUrl")
                        if content_url:
                            f_ext = determine_ext(content_url)
                            formats.append(
                                MediaFormat(
                                    format_id=f"jsonld-{len(formats)}",
                                    url=urljoin(url, content_url),
                                    ext=f_ext,
                                    width=int_or_none(item.get("width")),
                                    height=int_or_none(item.get("height")),
                                )
                            )
            except Exception:
                pass

        # 2. OpenGraph video/audio meta
        og_video = self._html_search_meta(["og:video", "og:video:secure_url", "twitter:player:stream"], html_doc)
        if og_video:
            formats.append(
                MediaFormat(
                    format_id=f"og-video-{len(formats)}",
                    url=urljoin(url, og_video),
                    ext=determine_ext(og_video),
                )
            )

        og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url"], html_doc)
        if og_audio:
            formats.append(
                MediaFormat(
                    format_id=f"og-audio-{len(formats)}",
                    url=urljoin(url, og_audio),
                    ext=determine_ext(og_audio, "mp3"),
                    vcodec="none",
                )
            )

        # 3. HTML5 <video> & <audio> & <source> tags
        media_tags = re.findall(
            r'<(?:video|audio|source)[^>]+src=["\']([^"\']+)["\'][^>]*>',
            html_doc,
            re.IGNORECASE,
        )
        for m_src in media_tags:
            full_src = urljoin(url, m_src)
            f_ext = determine_ext(full_src)
            if full_src not in [f.url for f in formats]:
                if f_ext == "m3u8":
                    formats.extend(self._extract_m3u8_formats(full_src, stem))
                elif f_ext == "mpd":
                    formats.extend(self._extract_mpd_formats(full_src, stem))
                else:
                    formats.append(
                        MediaFormat(
                            format_id=f"html5-{len(formats)}",
                            url=full_src,
                            ext=f_ext,
                        )
                    )

        # Fallback if no media tags found
        if not formats:
            formats.append(
                MediaFormat(
                    format_id="direct",
                    url=url,
                    ext=ext,
                )
            )

        return MediaInfo(
            id=stem or url_hash,
            title=title or f"Media [{stem}]",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            url=formats[0].url if formats else url,
            description=description,
            thumbnail=thumbnails[0].url if thumbnails else None,
            thumbnails=thumbnails,
            duration=duration,
            formats=formats,
        )
