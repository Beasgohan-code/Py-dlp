"""Universal AI & Heuristic Media Extractor for Py-dlp.

Capable of extracting video, audio, HLS/DASH streams, embedded players,
and metadata from any webpage across the entire Internet.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import Chapter, MediaFormat, MediaInfo, MediaSubtitle, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration, urljoin
from pydlp.extractor.base import InfoExtractor

_DIRECT_EXT_RE = re.compile(
    r"\.(mp4|m4v|mkv|webm|flv|avi|mov|ts|m3u8|mpd|mp3|m4a|aac|ogg|opus|flac|wav)(\?.*)?$",
    re.IGNORECASE,
)

_IFRAME_EMBED_PATTERNS = [
    (re.compile(r'(?:youtube\.com/embed/|youtube-nocookie\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', re.IGNORECASE), "https://www.youtube.com/watch?v={}"),
    (re.compile(r'player\.vimeo\.com/video/(\d+)', re.IGNORECASE), "https://vimeo.com/{}"),
    (re.compile(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', re.IGNORECASE), "https://www.dailymotion.com/video/{}"),
    (re.compile(r'streamable\.com/(?:e/)?([a-zA-Z0-9]+)', re.IGNORECASE), "https://streamable.com/{}"),
    (re.compile(r'rumble\.com/embed/([a-zA-Z0-9_-]+)', re.IGNORECASE), "https://rumble.com/embed/{}/"),
    (re.compile(r'bilibili\.com/blackboard/html5mobileplayer\.html\?bvid=([a-zA-Z0-9]+)', re.IGNORECASE), "https://www.bilibili.com/video/{}"),
    (re.compile(r'fast\.wistia\.net/embed/iframe/([a-zA-Z0-9]+)', re.IGNORECASE), "https://fast.wistia.net/embed/iframe/{}"),
    (re.compile(r'loom\.com/embed/([a-zA-Z0-9]+)', re.IGNORECASE), "https://www.loom.com/share/{}"),
]

_STREAM_URL_RE = re.compile(
    r'["\'](https?://[^"\']+\.(?:m3u8|mpd|mp4|webm|m4a|mp3|opus|flac|wav)(?:\?[^"\']*)?)["\']',
    re.IGNORECASE,
)


class UniversalExtractor(InfoExtractor):
    """The Universal Media Engine extracting streams from any website on the Internet."""

    IE_NAME = "generic"
    IE_DESC = "Universal Webpage & Direct Stream Extractor"
    _VALID_URL = r".+"

    def _real_extract(self, url: str) -> MediaInfo:
        path = urllib.parse.urlparse(url).path
        ext = determine_ext(url)
        stem = os.path.splitext(os.path.basename(path))[0] or "media"
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]

        # 1. Direct Media URL Check
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

        # 2. Download and Analyze Webpage
        html_doc = self._download_webpage(url, video_id=stem, fatal=False)
        if not html_doc:
            return MediaInfo(
                id=url_hash,
                title=f"Direct Media [{url_hash}]",
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=url,
                url=url,
                formats=[MediaFormat(format_id="http-0", url=url, ext=ext or "mp4")],
            )

        # 3. Check for Embedded IFrame Players & Delegate
        for pattern, url_tmpl in _IFRAME_EMBED_PATTERNS:
            m = pattern.search(html_doc)
            if m:
                target_url = url_tmpl.format(m.group(1))
                try:
                    from pydlp.extractor import find_extractor_for_url
                    sub_ie = find_extractor_for_url(target_url, self.http, self.options)
                    if sub_ie.IE_NAME != self.IE_NAME:
                        return sub_ie.extract(target_url)
                except Exception:
                    pass

        # 4. Extract Metadata
        title = (
            self._html_search_meta(["og:title", "twitter:title"], html_doc)
            or self._html_search_regex(r"<title>([^<]+)</title>", html_doc, "title", default=None)
            or stem
        )
        title = clean_html(title)

        description = self._html_search_meta(
            ["og:description", "twitter:description", "description"], html_doc
        )
        uploader = self._html_search_meta(
            ["author", "og:article:author", "article:author", "uploader"], html_doc
        )
        upload_date = self._html_search_meta(
            ["upload_date", "datePublished", "article:published_time"], html_doc
        )
        if upload_date and len(upload_date) >= 10:
            upload_date = upload_date[:10].replace("-", "")

        thumb_url = self._html_search_meta(["og:image", "twitter:image"], html_doc)
        thumbnail = urljoin(url, thumb_url) if thumb_url else None
        thumbnails = [MediaThumbnail(url=thumbnail)] if thumbnail else []

        duration_str = self._html_search_meta(["video:duration", "music:duration"], html_doc)
        duration = parse_duration(duration_str)

        formats: List[MediaFormat] = []
        subtitles: Dict[str, List[MediaSubtitle]] = {}
        chapters: List[Chapter] = []

        # 5. Extract JSON-LD Schema.org Data
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
                    if itype in ("VideoObject", "AudioObject", "MediaObject", "Movie", "TVEpisode"):
                        title = item.get("name") or item.get("headline") or title
                        description = item.get("description") or description
                        jld_thumb = item.get("thumbnailUrl")
                        if jld_thumb:
                            thumbnail = urljoin(url, jld_thumb)
                            if not any(t.url == thumbnail for t in thumbnails):
                                thumbnails.insert(0, MediaThumbnail(url=thumbnail))
                        upload_date = item.get("uploadDate") or upload_date
                        if not duration and item.get("duration"):
                            duration = parse_duration(item.get("duration"))
                        content_url = item.get("contentUrl") or item.get("embedUrl")
                        if content_url:
                            f_url = urljoin(url, content_url)
                            f_ext = determine_ext(f_url)
                            if f_ext == "m3u8":
                                m3u8_fmts = self._extract_m3u8_formats(f_url, stem)
                                if m3u8_fmts:
                                    formats.extend(m3u8_fmts)
                                else:
                                    formats.append(
                                        MediaFormat(
                                            format_id=f"jsonld-hls-{len(formats)}",
                                            url=f_url,
                                            ext="mp4",
                                            protocol="m3u8_native",
                                        )
                                    )
                            elif f_ext == "mpd":
                                formats.extend(self._extract_mpd_formats(f_url, stem))
                            else:
                                formats.append(
                                    MediaFormat(
                                        format_id=f"jsonld-{len(formats)}",
                                        url=f_url,
                                        ext=f_ext,
                                        width=int_or_none(item.get("width")),
                                        height=int_or_none(item.get("height")),
                                    )
                                )
            except Exception:
                pass

        # 6. OpenGraph & Twitter Player Streams
        for og_key in ["og:video", "og:video:url", "og:video:secure_url", "twitter:player:stream"]:
            og_v = self._html_search_meta(og_key, html_doc)
            if og_v and urljoin(url, og_v) not in [f.url for f in formats]:
                formats.append(
                    MediaFormat(
                        format_id=f"og-video-{len(formats)}",
                        url=urljoin(url, og_v),
                        ext=determine_ext(og_v, "mp4"),
                    )
                )

        og_audio = self._html_search_meta(["og:audio", "og:audio:secure_url"], html_doc)
        if og_audio and urljoin(url, og_audio) not in [f.url for f in formats]:
            formats.append(
                MediaFormat(
                    format_id=f"og-audio-{len(formats)}",
                    url=urljoin(url, og_audio),
                    ext=determine_ext(og_audio, "mp3"),
                    vcodec="none",
                )
            )

        # 7. HTML5 Media & Source Tags
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
                    m3u8_fmts = self._extract_m3u8_formats(full_src, stem)
                    if m3u8_fmts:
                        formats.extend(m3u8_fmts)
                    else:
                        formats.append(
                            MediaFormat(
                                format_id=f"hls-{len(formats)}",
                                url=full_src,
                                ext="mp4",
                                protocol="m3u8_native",
                            )
                        )
                elif f_ext == "mpd":
                    formats.extend(self._extract_mpd_formats(full_src, stem))
                else:
                    formats.append(
                        MediaFormat(
                            format_id=f"html5-{len(formats)}",
                            url=full_src,
                            ext=f_ext or "mp4",
                        )
                    )

        # 8. HTML5 Subtitles / Captions Track Discovery
        track_tags = re.findall(
            r'<track[^>]+src=["\']([^"\']+)["\'][^>]*>',
            html_doc,
            re.IGNORECASE,
        )
        for t_src in track_tags:
            t_url = urljoin(url, t_src)
            lang = "en"
            subtitles.setdefault(lang, []).append(
                MediaSubtitle(url=t_url, ext=determine_ext(t_url, "vtt"), language=lang)
            )

        # 9. Deep In-Page JavaScript Manifest & Stream URL Sniffer
        for m in _STREAM_URL_RE.finditer(html_doc):
            found_url = m.group(1)
            f_url = urljoin(url, found_url)
            f_ext = determine_ext(f_url)
            if f_url not in [f.url for f in formats]:
                if f_ext == "m3u8":
                    m3u8_fmts = self._extract_m3u8_formats(f_url, stem)
                    if m3u8_fmts:
                        formats.extend(m3u8_fmts)
                    else:
                        formats.append(
                            MediaFormat(
                                format_id=f"stream-{len(formats)}",
                                url=f_url,
                                ext="mp4",
                                protocol="m3u8_native",
                            )
                        )
                elif f_ext == "mpd":
                    formats.extend(self._extract_mpd_formats(f_url, stem))
                elif f_ext in ("mp4", "webm", "m4a", "mp3", "flac", "opus", "wav"):
                    formats.append(
                        MediaFormat(
                            format_id=f"stream-{len(formats)}",
                            url=f_url,
                            ext=f_ext,
                        )
                    )

        # 10. Auto Chapters Discovery from Timestamps in Description
        if description:
            chapter_matches = re.findall(r"(?:^|\n)\s*(\d{1,2}:\d{2}(?::\d{2})?)\s+([^\n]+)", description)
            for ts_str, ch_title in chapter_matches:
                t_sec = parse_duration(ts_str)
                if t_sec is not None:
                    chapters.append(Chapter(start_time=t_sec, title=ch_title.strip()))
            # Sort chapters by start time
            chapters.sort(key=lambda c: c.start_time)

        # Fallback if no media streams were detected
        if not formats:
            formats.append(
                MediaFormat(
                    format_id="direct",
                    url=url,
                    ext=ext or "mp4",
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
            uploader=uploader,
            upload_date=upload_date,
            thumbnail=thumbnails[0].url if thumbnails else None,
            thumbnails=thumbnails,
            duration=duration,
            formats=formats,
            subtitles=subtitles,
            chapters=chapters,
        )


# Alias for backward compatibility
GenericIE = UniversalExtractor
