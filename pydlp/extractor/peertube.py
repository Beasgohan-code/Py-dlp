"""PeerTube and Fediverse video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List
import urllib.parse

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, parse_duration, try_get, urljoin
from pydlp.extractor.base import InfoExtractor


class PeerTubeIE(InfoExtractor):
    """Extractor for PeerTube instances across the Fediverse."""

    IE_NAME = "peertube"
    IE_DESC = "PeerTube federated video platforms"
    _VALID_URL = r"^(?:https?://)?(?P<host>[^/]+)/(?:videos/watch/|w/|api/v1/videos/)(?P<id>[a-zA-Z0-9-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        host = m.group("host")
        video_id = m.group("id")

        api_url = f"https://{host}/api/v1/videos/{video_id}"
        info = self._download_json(api_url, video_id=video_id, fatal=False)

        if not info:
            # Fallback webpage scraping
            webpage = self._download_webpage(url, video_id=video_id, fatal=False)
            og_title = self._html_search_meta(["og:title"], webpage, default=f"PeerTube Video {video_id}")
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            return MediaInfo(
                id=video_id,
                title=og_title,
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=url,
                formats=[MediaFormat(format_id="og-video", url=og_video or url, ext="mp4")],
            )

        title = info.get("name", f"PeerTube Video {video_id}")
        description = info.get("description")
        uploader = try_get(info, lambda x: x["account"]["displayName"], str) or try_get(info, lambda x: x["account"]["name"], str)
        channel = try_get(info, lambda x: x["channel"]["displayName"], str)
        duration = float(info.get("duration", 0)) if info.get("duration") else None
        view_count = int_or_none(info.get("views"))
        thumbnail = urljoin(f"https://{host}", info.get("thumbnailPath", "")) if info.get("thumbnailPath") else None

        formats: List[MediaFormat] = []

        # Direct WebTorrent / MP4 files
        for f in info.get("files", []):
            f_url = f.get("fileUrl") or f.get("fileDownloadUrl")
            if f_url:
                res_label = try_get(f, lambda x: x["resolution"]["label"], str) or "file"
                height = int_or_none(try_get(f, lambda x: x["resolution"]["id"]))
                fps = float(f.get("fps", 30))
                size = int_or_none(f.get("size"))
                formats.append(
                    MediaFormat(
                        format_id=f"http-{res_label}",
                        url=f_url,
                        ext="mp4",
                        height=height,
                        fps=fps,
                        filesize=size,
                        format_note=res_label,
                    )
                )

        # HLS / Streaming playlists
        for pl in info.get("streamingPlaylists", []):
            pl_url = pl.get("playlistUrl")
            if pl_url:
                formats.extend(self._extract_m3u8_formats(pl_url, video_id, note="HLS"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://{host}/videos/watch/{video_id}",
            description=description,
            uploader=uploader,
            channel=channel,
            duration=duration,
            view_count=view_count,
            thumbnail=thumbnail,
            formats=formats,
        )
