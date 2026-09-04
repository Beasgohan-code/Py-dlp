"""Google Drive and Dropbox media extractor."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class GDriveIE(InfoExtractor):
    """Extractor for Google Drive and Dropbox shared media files."""

    IE_NAME = "gdrive"
    IE_DESC = "Google Drive and Dropbox shared media"
    _VALID_URL = r"^(?:https?://)?(?:drive\.google\.com/(?:file/d/|open\?id=)|docs\.google\.com/file/d/)(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        file_id = self._match_id(url)
        webpage_url = f"https://drive.google.com/file/d/{file_id}/view"
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        webpage = self._download_webpage(webpage_url, video_id=file_id, fatal=False)
        title = f"Google Drive File {file_id}"
        thumbnail = f"https://drive.google.com/thumbnail?id={file_id}"

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            if og_title:
                title = clean_html(og_title)

        formats = [
            MediaFormat(
                format_id="direct-download",
                url=download_url,
                ext="mp4",
                format_note="Full Quality Original",
            )
        ]

        return MediaInfo(
            id=file_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=webpage_url,
            thumbnail=thumbnail,
            formats=formats,
        )
