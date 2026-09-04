"""Download Archive management to prevent redundant downloads."""

from __future__ import annotations

import os
from typing import Optional, Set

from pydlp.core.types import MediaInfo


class DownloadArchive:
    """Manages persistent archive file of downloaded media IDs to skip duplicates."""

    def __init__(self, archive_file: Optional[str] = None):
        self.archive_file = archive_file
        self.downloaded_ids: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self.archive_file or not os.path.isfile(self.archive_file):
            return
        try:
            with open(self.archive_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.downloaded_ids.add(line)
        except Exception:
            pass

    def contains(self, info: MediaInfo) -> bool:
        if not self.archive_file:
            return False
        ie_key = info.extractor_key or info.extractor or "generic"
        media_id = info.id
        entry = f"{ie_key} {media_id}"
        alt_entry = f"{info.extractor} {media_id}"
        return (entry in self.downloaded_ids) or (alt_entry in self.downloaded_ids) or (media_id in self.downloaded_ids)

    def record(self, info: MediaInfo) -> None:
        if not self.archive_file:
            return
        ie_key = info.extractor_key or info.extractor or "generic"
        media_id = info.id
        entry = f"{ie_key} {media_id}"
        self.downloaded_ids.add(entry)
        try:
            dirname = os.path.dirname(self.archive_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(self.archive_file, "a", encoding="utf-8") as f:
                f.write(f"{entry}\n")
        except Exception:
            pass
