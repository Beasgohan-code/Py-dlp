"""Metadata embedding and .info.json export post-processor."""

from __future__ import annotations

import json
import os
import struct
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import has_ffmpeg


def build_id3v2_tag(title: str, artist: str = "", album: str = "", year: str = "") -> bytes:
    """Builds a basic ID3v2.3 tag header and text frames in pure Python."""
    frames_bytes = bytearray()

    def add_text_frame(frame_id: str, text: str):
        if not text:
            return
        enc_text = text.encode("utf-8")
        # Frame payload: 0x03 (UTF-8 encoding flag) + text bytes
        payload = b"\x03" + enc_text
        size = len(payload)
        # 4 bytes frame ID + 4 bytes size + 2 bytes flags (0x0000)
        frame_header = frame_id.encode("ascii") + struct.pack(">I", size) + b"\x00\x00"
        frames_bytes.extend(frame_header + payload)

    add_text_frame("TIT2", title)
    add_text_frame("TPE1", artist)
    add_text_frame("TALB", album)
    add_text_frame("TYER", year)

    # Calculate syncsafe size (28-bit integer split across 4 bytes, 7 bits per byte)
    tag_size = len(frames_bytes)
    b1 = (tag_size >> 21) & 0x7F
    b2 = (tag_size >> 14) & 0x7F
    b3 = (tag_size >> 7) & 0x7F
    b4 = tag_size & 0x7F

    # ID3v2 header: 'ID3' (3 bytes), version 2.3 (0x03 0x00), flags (0x00), size (4 syncsafe bytes)
    header = b"ID3\x03\x00\x00" + bytes([b1, b2, b3, b4])
    return header + frames_bytes


class MetadataPostProcessor(BasePostProcessor):
    """Embeds media metadata tags and writes metadata info JSON files."""

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        filepath = info.filepath or info.filename
        if not filepath or not os.path.exists(filepath):
            return files_to_delete, info

        base_stem, ext = os.path.splitext(filepath)

        # 1. Write .info.json if requested
        if self.options.get("writeinfojson", False):
            info_json_path = f"{base_stem}.info.json"
            try:
                with open(info_json_path, "w", encoding="utf-8") as f:
                    json.dump(info.to_dict(), f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        # 2. Embed metadata tags if requested
        if self.options.get("addmetadata", False):
            title = info.title or "Unknown"
            artist = info.uploader or info.channel or ""
            album = info.playlist_title or ""
            year = info.upload_date[:4] if info.upload_date and len(info.upload_date) >= 4 else ""

            if ext.lower() == ".mp3":
                try:
                    # Prepend ID3v2 tag if not present
                    with open(filepath, "rb") as f:
                        content = f.read()

                    if not content.startswith(b"ID3"):
                        id3_tag = build_id3v2_tag(title, artist, album, year)
                        with open(filepath, "wb") as f:
                            f.write(id3_tag + content)
                except Exception:
                    pass

        return files_to_delete, info
