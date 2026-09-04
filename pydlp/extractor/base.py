"""Base extractor class providing common scraping, parsing, and extraction helpers."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pydlp.core.exceptions import ExtractorError
from pydlp.core.format_selector import sort_formats
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaChapter, MediaFormat, MediaInfo, MediaSubtitle, MediaThumbnail
from pydlp.core.utils import (
    clean_html,
    determine_ext,
    float_or_none,
    int_or_none,
    parse_duration,
    parse_iso8601,
    parse_m3u8_attributes,
    str_or_none,
    try_get,
    unescape_html,
    urljoin,
)


class InfoExtractor:
    """Base class for all media extractors."""

    IE_NAME: str = "generic"
    IE_DESC: Optional[str] = None
    _VALID_URL: str = r""
    SEARCH_KEY: Optional[str] = None

    def __init__(self, http_client: Optional[HttpClient] = None, options: Optional[Dict[str, Any]] = None):
        self.http = http_client or HttpClient()
        self.options = options or {}
        self._cache = getattr(self.http, "cache", None)

    @classmethod
    def ie_key(cls) -> str:
        return cls.IE_NAME or cls.__name__.replace("IE", "")

    @classmethod
    def suitable(cls, url: str) -> bool:
        if not cls._VALID_URL:
            return False
        return re.match(cls._VALID_URL, url, re.IGNORECASE) is not None

    def _match_id(self, url: str) -> str:
        m = re.match(self._VALID_URL, url, re.IGNORECASE)
        if not m:
            raise ExtractorError(f"URL does not match {self.IE_NAME} pattern: {url}", expected=True)
        id_group = m.groupdict().get("id")
        if id_group:
            return id_group
        return m.group(1) if m.groups() else "default"

    def _download_webpage(
        self,
        url: str,
        video_id: Optional[str] = None,
        note: Optional[str] = None,
        errnote: Optional[str] = None,
        fatal: bool = True,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            resp = self.http.get(url, headers=headers, params=params)
            return resp.text()
        except Exception as e:
            if fatal:
                msg = errnote or f"Failed to download webpage for {video_id or url}"
                raise ExtractorError(msg, orig_error=e, video_id=video_id, ie=self.IE_NAME)
            return ""

    def _download_json(
        self,
        url: str,
        video_id: Optional[str] = None,
        note: Optional[str] = None,
        errnote: Optional[str] = None,
        fatal: bool = True,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[bytes, str, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            if data is not None:
                resp = self.http.post(url, headers=headers, data=data, params=params)
            else:
                resp = self.http.get(url, headers=headers, params=params)
            return resp.json()
        except Exception as e:
            if fatal:
                msg = errnote or f"Failed to download JSON for {video_id or url}"
                raise ExtractorError(msg, orig_error=e, video_id=video_id, ie=self.IE_NAME)
            return None

    def _search_regex(
        self,
        pattern: Union[str, List[str]],
        string: str,
        name: str,
        default: Any = "_NO_DEFAULT_",
        fatal: bool = True,
        flags: int = 0,
        group: Union[int, str] = 1,
    ) -> Optional[str]:
        if isinstance(pattern, str):
            patterns = [pattern]
        else:
            patterns = pattern

        for p in patterns:
            m = re.search(p, string, flags)
            if m:
                try:
                    return m.group(group)
                except IndexError:
                    return m.group(0)

        if default != "_NO_DEFAULT_":
            return default
        if fatal:
            raise ExtractorError(f"Unable to extract {name}", ie=self.IE_NAME)
        return None

    def _html_search_regex(
        self,
        pattern: Union[str, List[str]],
        string: str,
        name: str,
        default: Any = "_NO_DEFAULT_",
        fatal: bool = True,
        flags: int = 0,
        group: Union[int, str] = 1,
    ) -> Optional[str]:
        res = self._search_regex(pattern, string, name, default=default, fatal=fatal, flags=flags, group=group)
        return clean_html(res) if res is not None else None

    def _html_search_meta(
        self,
        name: Union[str, List[str]],
        html_text: str,
        default: Any = None,
        fatal: bool = False,
    ) -> Optional[str]:
        if isinstance(name, str):
            names = [name]
        else:
            names = name

        for n in names:
            pattern = (
                rf'<meta[^>]+(?:name|property|itemprop)=["\']{re.escape(n)}["\'][^>]+content=["\']([^"\']*)["\']'
            )
            m = re.search(pattern, html_text, re.IGNORECASE)
            if not m:
                # Alternate attribute order
                pattern_alt = (
                    rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:name|property|itemprop)=["\']{re.escape(n)}["\']'
                )
                m = re.search(pattern_alt, html_text, re.IGNORECASE)
            if m:
                return unescape_html(m.group(1).strip())

        if fatal:
            raise ExtractorError(f"Unable to find meta tag for {names[0]}", ie=self.IE_NAME)
        return default

    def _parse_json(
        self,
        json_string: str,
        video_id: Optional[str] = None,
        fatal: bool = True,
    ) -> Any:
        try:
            return json.loads(json_string)
        except Exception as e:
            if fatal:
                raise ExtractorError(f"Failed to parse JSON: {e}", video_id=video_id, ie=self.IE_NAME)
            return None

    def _extract_m3u8_formats(
        self,
        m3u8_url: str,
        video_id: str,
        ext: str = "mp4",
        note: Optional[str] = None,
        fatal: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[MediaFormat]:
        """Parses an M3U8 master playlist and extracts variant format streams."""
        formats: List[MediaFormat] = []
        try:
            resp = self.http.get(m3u8_url, headers=headers)
            content = resp.text()
        except Exception as e:
            if fatal:
                raise ExtractorError(f"Failed to fetch M3U8 manifest: {e}", orig_error=e, video_id=video_id)
            return formats

        lines = [line.strip() for line in content.splitlines() if line.strip()]

        if not any(l.startswith("#EXT-X-STREAM-INF:") for l in lines):
            # Single stream media playlist
            formats.append(
                MediaFormat(
                    format_id="hls-default",
                    url=m3u8_url,
                    ext=ext,
                    protocol="m3u8_native",
                    format_note=note or "HLS stream",
                )
            )
            return formats

        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF:") and i + 1 < len(lines):
                attrs = parse_m3u8_attributes(line[18:])
                stream_url = lines[i + 1].strip()
                if not stream_url.startswith("#"):
                    stream_full_url = urljoin(m3u8_url, stream_url)
                    bandwidth = int_or_none(attrs.get("BANDWIDTH"))
                    tbr = round(bandwidth / 1000.0) if bandwidth else None

                    resolution = attrs.get("RESOLUTION")
                    width = None
                    height = None
                    if resolution and "x" in resolution:
                        w_s, h_s = resolution.split("x", 1)
                        width = int_or_none(w_s)
                        height = int_or_none(h_s)

                    frame_rate = float_or_none(attrs.get("FRAME-RATE"))
                    codecs = attrs.get("CODECS", "")
                    vcodec = None
                    acodec = None
                    if codecs:
                        c_list = [c.strip() for c in codecs.split(",")]
                        for c in c_list:
                            if c.startswith(("avc", "mp4v", "hev", "hvc", "vp9", "av01")):
                                vcodec = c
                            elif c.startswith(("mp4a", "ac-3", "ec-3", "opus")):
                                acodec = c

                    fmt_id = f"hls-{height}p" if height else (f"hls-{tbr}k" if tbr else f"hls-{len(formats)}")
                    formats.append(
                        MediaFormat(
                            format_id=fmt_id,
                            url=stream_full_url,
                            ext=ext,
                            width=width,
                            height=height,
                            fps=frame_rate,
                            vcodec=vcodec,
                            acodec=acodec,
                            tbr=float(tbr) if tbr else None,
                            protocol="m3u8_native",
                            format_note=attrs.get("NAME"),
                        )
                    )

        return formats

    def _extract_mpd_formats(
        self,
        mpd_url: str,
        video_id: str,
        fatal: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[MediaFormat]:
        """Parses an MPEG-DASH MPD manifest and extracts representation formats."""
        formats: List[MediaFormat] = []
        try:
            resp = self.http.get(mpd_url, headers=headers)
            content = resp.text()
        except Exception as e:
            if fatal:
                raise ExtractorError(f"Failed to fetch MPD manifest: {e}", orig_error=e, video_id=video_id)
            return formats

        # Fallback format entry pointing to manifest
        formats.append(
            MediaFormat(
                format_id="dash-manifest",
                url=mpd_url,
                ext="mp4",
                protocol="dash",
                format_note="MPEG-DASH stream",
            )
        )
        return formats

    def _sort_formats(self, formats: List[MediaFormat]) -> List[MediaFormat]:
        return sort_formats(formats)

    def extract(self, url: str) -> MediaInfo:
        """Main extraction entrypoint."""
        info = self._real_extract(url)
        if not info.webpage_url:
            info.webpage_url = url
        if not info.extractor:
            info.extractor = self.IE_NAME
        if not info.extractor_key:
            info.extractor_key = self.ie_key()
        if info.formats:
            info.formats = self._sort_formats(info.formats)
            if not info.ext and info.formats:
                info.ext = info.formats[-1].ext
        return info

    def _real_extract(self, url: str) -> MediaInfo:
        raise NotImplementedError()
