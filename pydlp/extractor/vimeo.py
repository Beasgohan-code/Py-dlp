"""Vimeo video and showcase extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class VimeoIE(InfoExtractor):
    """Extractor for Vimeo videos."""

    IE_NAME = "vimeo"
    IE_DESC = "Vimeo.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|player\.)?vimeo\.com/(?:channels/(?:\w+/)?|groups/[^/]+/videos/|album/(?:\d+/)?video/|video/|)(\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        config_url = f"https://player.vimeo.com/video/{video_id}/config"
        config = self._download_json(config_url, video_id=video_id, fatal=False)

        if not config or "request" not in config:
            # Fallback direct HTML page parsing
            webpage = self._download_webpage(f"https://vimeo.com/{video_id}", video_id=video_id, fatal=False)
            title = self._html_search_meta(["og:title"], webpage, default=f"Vimeo Video {video_id}")
            thumb = self._html_search_meta(["og:image"], webpage)
            return MediaInfo(
                id=video_id,
                title=title,
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=f"https://vimeo.com/{video_id}",
                thumbnail=thumb,
                formats=[
                    MediaFormat(
                        format_id="hls-default",
                        url=f"https://skyfire.vimeocdn.com/live/{video_id}/master.m3u8",
                        ext="mp4",
                        protocol="m3u8_native",
                    )
                ],
            )

        video_info = config.get("video", {})
        title = video_info.get("title", f"Vimeo Video {video_id}")
        duration = float(video_info.get("duration", 0)) if video_info.get("duration") else None
        uploader = try_get(video_info, lambda x: x["owner"]["name"], str)
        uploader_url = try_get(video_info, lambda x: x["owner"]["url"], str)
        thumbnail = video_info.get("thumbs", {}).get("base")

        formats: List[MediaFormat] = []
        files = try_get(config, lambda x: x["request"]["files"], dict) or {}

        # Progressive MP4 formats
        for p in files.get("progressive", []):
            url_p = p.get("url")
            if not url_p:
                continue
            quality = p.get("quality", "sd")
            width = int_or_none(p.get("width"))
            height = int_or_none(p.get("height"))
            fps = int_or_none(p.get("fps"))

            formats.append(
                MediaFormat(
                    format_id=f"http-{quality}",
                    url=url_p,
                    ext="mp4",
                    width=width,
                    height=height,
                    fps=float(fps) if fps else None,
                    format_note=quality,
                    protocol="https",
                )
            )

        # HLS stream
        hls_info = files.get("hls", {})
        cdns = hls_info.get("cdns", {})
        for cdn_name, cdn_data in cdns.items():
            hls_url = cdn_data.get("url")
            if hls_url:
                formats.extend(self._extract_m3u8_formats(hls_url, video_id, note=f"HLS ({cdn_name})"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://vimeo.com/{video_id}",
            duration=duration,
            uploader=uploader,
            uploader_url=uploader_url,
            thumbnail=thumbnail,
            formats=formats,
        )
