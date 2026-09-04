"""Thumbnail downloading and artwork post-processor."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaInfo
from pydlp.core.utils import determine_ext
from pydlp.postprocessor.base import BasePostProcessor


class ThumbnailPostProcessor(BasePostProcessor):
    """Downloads thumbnail artwork images alongside media files."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.http = http_client

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        if not self.options.get("writethumbnail", False) and not self.options.get("writeallthumbnails", False):
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath:
            return files_to_delete, info

        base_stem, _ = os.path.splitext(filepath)
        thumb_url = info.thumbnail or (info.thumbnails[-1].url if info.thumbnails else None)

        if thumb_url:
            ext = determine_ext(thumb_url, "jpg")
            out_thumb_path = f"{base_stem}.{ext}"
            try:
                resp = self.http.get(thumb_url)
                with open(out_thumb_path, "wb") as f:
                    f.write(resp.content)
            except Exception:
                pass

        return files_to_delete, info
