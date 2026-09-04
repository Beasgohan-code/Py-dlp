"""yt-dlp compatibility InfoExtractor shim."""

from __future__ import annotations

import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Union

from pydlp.compat.yt_dlp.utils import (
    ExtractorError,
    clean_html,
    determine_ext,
    float_or_none,
    int_or_none,
    js_to_json,
    parse_duration,
    parse_iso8601,
    str_or_none,
    traverse_obj,
    unescape_html,
    url_or_none,
    urljoin,
)
from pydlp.core.exceptions import ExtractorError
from pydlp.core.format_selector import sort_formats
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaChapter, MediaFormat, MediaInfo, MediaSubtitle, MediaThumbnail
from pydlp.extractor.base import InfoExtractor as PyDLPBaseExtractor


class InfoExtractor(PyDLPBaseExtractor):
    """Compatibility base class allowing yt-dlp extractors to run seamlessly inside Py-dlp."""

    IE_NAME: str = "generic"
    _VALID_URL: str = r""

    def __init__(self, http_client: Optional[HttpClient] = None, options: Optional[Dict[str, Any]] = None):
        if http_client is None:
            http_client = HttpClient()
        super().__init__(http_client, options)

    def _proto_relative_url(self, url: Optional[str], scheme: str = "https:") -> Optional[str]:
        if not url:
            return url
        if url.startswith("//"):
            return scheme + url
        return url

    def _request_webpage(
        self,
        url_or_request: Any,
        video_id: Optional[str] = None,
        note: Optional[str] = None,
        errnote: Optional[str] = None,
        fatal: bool = True,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, Any]] = None,
        expected_status: Optional[Union[int, List[int]]] = None,
    ) -> Any:
        url = url_or_request if isinstance(url_or_request, str) else getattr(url_or_request, "url", str(url_or_request))
        try:
            if data is not None:
                resp = self.http.post(url, headers=headers, data=data, params=query)
            else:
                resp = self.http.get(url, headers=headers, params=query)
            return resp
        except Exception as e:
            if fatal:
                raise ExtractorError(errnote or f"Failed to request {url}", orig_error=e, video_id=video_id)
            return None

    def _download_webpage_handle(
        self,
        url: str,
        video_id: Optional[str] = None,
        note: Optional[str] = None,
        errnote: Optional[str] = None,
        fatal: bool = True,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, Any]] = None,
        expected_status: Optional[Union[int, List[int]]] = None,
    ) -> Tuple[str, Any]:
        resp = self._request_webpage(url, video_id, note, errnote, fatal, data, headers, query, expected_status)
        if resp is not None:
            return resp.text(), resp
        return "", None

    def _real_extract(self, url: str) -> Union[MediaInfo, Dict[str, Any]]:
        raise NotImplementedError()

    def extract(self, url: str) -> MediaInfo:
        """Entrypoint converting dictionary-based or dataclass-based extraction into MediaInfo."""
        res = self._real_extract(url)
        if isinstance(res, MediaInfo):
            info = res
        elif isinstance(res, dict):
            # Convert dictionary result from yt-dlp format
            formats: List[MediaFormat] = []
            for f in res.get("formats", []):
                if isinstance(f, MediaFormat):
                    formats.append(f)
                elif isinstance(f, dict):
                    formats.append(
                        MediaFormat(
                            format_id=str(f.get("format_id", "0")),
                            url=f.get("url", ""),
                            ext=f.get("ext", "mp4"),
                            width=int_or_none(f.get("width")),
                            height=int_or_none(f.get("height")),
                            fps=float_or_none(f.get("fps")),
                            vcodec=f.get("vcodec"),
                            acodec=f.get("acodec"),
                            tbr=float_or_none(f.get("tbr")),
                            vbr=float_or_none(f.get("vbr")),
                            abr=float_or_none(f.get("abr")),
                            filesize=int_or_none(f.get("filesize") or f.get("filesize_approx")),
                            protocol=f.get("protocol", "https"),
                            http_headers=f.get("http_headers", {}),
                            format_note=f.get("format_note"),
                        )
                    )
                elif isinstance(f, str):
                    formats.append(MediaFormat(format_id="direct", url=f, ext=determine_ext(f)))

            if not formats and res.get("url"):
                formats.append(
                    MediaFormat(
                        format_id="0",
                        url=res["url"],
                        ext=res.get("ext", determine_ext(res["url"])),
                    )
                )

            subtitles: Dict[str, List[MediaSubtitle]] = {}
            for lang, subs in res.get("subtitles", {}).items():
                subtitles[lang] = [
                    MediaSubtitle(url=s.get("url", ""), ext=s.get("ext", "vtt"), name=s.get("name"))
                    for s in subs
                    if isinstance(s, dict) and s.get("url")
                ]

            thumbnails: List[MediaThumbnail] = []
            for t in res.get("thumbnails", []):
                if isinstance(t, dict) and t.get("url"):
                    thumbnails.append(
                        MediaThumbnail(
                            url=t["url"],
                            width=int_or_none(t.get("width")),
                            height=int_or_none(t.get("height")),
                        )
                    )
                elif isinstance(t, str):
                    thumbnails.append(MediaThumbnail(url=t))

            chapters: List[MediaChapter] = []
            for c in res.get("chapters", []):
                if isinstance(c, dict):
                    chapters.append(
                        MediaChapter(
                            start_time=float(c.get("start_time", 0.0)),
                            end_time=float(c.get("end_time", 0.0)),
                            title=c.get("title", ""),
                        )
                    )

            info = MediaInfo(
                id=str(res.get("id", "default")),
                title=res.get("title") or "Untitled Media",
                webpage_url=res.get("webpage_url") or url,
                description=res.get("description"),
                duration=float_or_none(res.get("duration")),
                thumbnail=res.get("thumbnail") or (thumbnails[0].url if thumbnails else None),
                uploader=res.get("uploader") or res.get("channel"),
                uploader_id=res.get("uploader_id") or res.get("channel_id"),
                upload_date=res.get("upload_date"),
                view_count=int_or_none(res.get("view_count")),
                like_count=int_or_none(res.get("like_count")),
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                formats=formats,
                subtitles=subtitles,
                thumbnails=thumbnails,
                chapters=chapters,
                ext=res.get("ext") or (formats[-1].ext if formats else "mp4"),
            )
        else:
            raise ExtractorError(f"Unexpected extraction return type: {type(res)}", ie=self.IE_NAME)

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
