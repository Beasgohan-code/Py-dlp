"""Internet Archive (archive.org) media extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class ArchiveOrgIE(InfoExtractor):
    """Extractor for Archive.org items and media collections."""

    IE_NAME = "archive.org"
    IE_DESC = "Internet Archive items and historical media"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?archive\.org/(?:details|embed)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        item_id = self._match_id(url)
        meta_url = f"https://archive.org/metadata/{item_id}"
        meta = self._download_json(meta_url, video_id=item_id, fatal=False)

        title = f"Internet Archive Item {item_id}"
        description = None
        uploader = None
        thumbnail = f"https://archive.org/services/img/{item_id}"
        duration = None
        formats: List[MediaFormat] = []

        if meta:
            metadata = meta.get("metadata", {})
            title = metadata.get("title") or title
            description = metadata.get("description")
            uploader = metadata.get("creator") or metadata.get("uploader")

            files = meta.get("files", [])
            server = meta.get("server", "ia600000.us.archive.org")
            dir_path = meta.get("dir", f"/items/{item_id}")

            for f in files:
                fname = f.get("name", "")
                f_format = f.get("format", "")
                f_size = int_or_none(f.get("size"))
                f_ext = determine_ext(fname)
                f_dur = parse_duration(f.get("length"))

                # Check if playable media file
                if f_ext in ("mp4", "mkv", "webm", "mp3", "flac", "ogg", "wav", "m4a", "ogv"):
                    file_url = f"https://{server}{dir_path}/{fname}"
                    is_audio = f_ext in ("mp3", "flac", "ogg", "wav", "m4a")
                    height = int_or_none(f.get("height"))
                    width = int_or_none(f.get("width"))

                    if f_dur and not duration:
                        duration = f_dur

                    formats.append(
                        MediaFormat(
                            format_id=clean_html(f_format).replace(" ", "_") or f_ext,
                            url=file_url,
                            ext=f_ext,
                            filesize=f_size,
                            width=width,
                            height=height,
                            vcodec="none" if is_audio else None,
                            acodec=f_ext if is_audio else None,
                            format_note=f_format,
                        )
                    )

        if not formats:
            # Fallback direct
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=item_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=f"https://archive.org/details/{item_id}",
            description=description,
            uploader=uploader,
            duration=duration,
            thumbnail=thumbnail,
            formats=formats,
        )
