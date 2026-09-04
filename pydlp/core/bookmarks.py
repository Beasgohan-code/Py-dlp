"""Netscape Bookmarks and M3U Playlist file importer for Py-dlp."""

from __future__ import annotations

import os
import re
from typing import List


class BookmarkImporter:
    """Extracts media and video links from Netscape HTML bookmarks and M3U playlist files."""

    @staticmethod
    def parse_html_bookmarks(filepath: str) -> List[str]:
        """Parse standard Netscape HTML bookmarks (exported from Chrome, Firefox, Edge, Safari, Brave)."""
        if not os.path.isfile(filepath):
            return []

        urls: List[str] = []
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Match <A HREF="url" ...>
        matches = re.findall(r'<A\s+(?:[^>]*?\s+)?HREF=["\'](https?://[^"\']+)["\']', content, re.IGNORECASE)
        for url in matches:
            url = url.strip()
            if url and url not in urls:
                urls.append(url)

        return urls

    @staticmethod
    def parse_m3u_playlist(filepath: str) -> List[str]:
        """Parse .m3u / .m3u8 playlist files for stream/media URLs."""
        if not os.path.isfile(filepath):
            return []

        urls: List[str] = []
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if line.startswith("http://") or line.startswith("https://") or line.startswith("rtmp://"):
                        if line not in urls:
                            urls.append(line)

        return urls

    @classmethod
    def import_file(cls, filepath: str) -> List[str]:
        """Auto-detect format and import URLs."""
        if not os.path.isfile(filepath):
            return []

        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".html", ".htm"):
            return cls.parse_html_bookmarks(filepath)
        elif ext in (".m3u", ".m3u8"):
            return cls.parse_m3u_playlist(filepath)
        else:
            # Fallback: check if content contains HTML
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                header = f.read(512)
            if "<!DOCTYPE NETSCAPE-Bookmark-file-1>" in header or "<A HREF=" in header.upper():
                return cls.parse_html_bookmarks(filepath)
            return cls.parse_m3u_playlist(filepath)
