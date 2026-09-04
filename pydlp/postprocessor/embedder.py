"""Unified Media Embedder PostProcessor for Py-dlp.

Embeds soft subtitles, thumbnail artwork, chapters, and metadata tags directly into output media files (MP4, MKV, MP3, M4A, FLAC, Opus).
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path

logger = logging.getLogger("pydlp.embedder")


class MediaEmbedderPostProcessor(BasePostProcessor):
    """Embeds subtitles, thumbnails, and metadata tags into the final container."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.embed_subs = self.options.get("embed_subs", False) or self.options.get("embed_subtitles", False)
        self.embed_thumbnail = self.options.get("embed_thumbnail", False)
        self.embed_metadata = self.options.get("embed_metadata", False) or self.options.get("add_metadata", False)
        self.embed_chapters = self.options.get("embed_chapters", False)

    @property
    def is_needed(self) -> bool:
        return bool(self.embed_subs or self.embed_thumbnail or self.embed_metadata or self.embed_chapters)

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.isfile(info.filepath):
            return [], info

        ffmpeg = get_ffmpeg_path()
        if not ffmpeg:
            logger.warning("[embedder] FFmpeg not found; skipping media embedding")
            return [], info

        base, ext = os.path.splitext(info.filepath)
        ext_clean = ext.lstrip(".").lower()
        out_filepath = f"{base}.embedded{ext}"

        # Build FFmpeg command
        cmd = [ffmpeg, "-y", "-i", info.filepath]
        input_idx = 1
        extra_maps: List[str] = ["-map", "0"]

        # 1. Embed Thumbnail Art
        thumb_path = f"{base}.jpg"
        if not os.path.isfile(thumb_path):
            thumb_path = f"{base}.webp"
        if not os.path.isfile(thumb_path):
            thumb_path = f"{base}.png"

        if self.embed_thumbnail and os.path.isfile(thumb_path):
            cmd.extend(["-i", thumb_path])
            extra_maps.extend(["-map", f"{input_idx}"])
            if ext_clean in ("mp4", "m4v", "mov"):
                cmd.extend([f"-c:v:{input_idx}", "copy", "-disposition:v:1", "attached_pic"])
            elif ext_clean == "mp3":
                cmd.extend(["-c:a", "copy", "-id3v2_version", "3", "-metadata:s:v", 'title="Album cover"', "-metadata:s:v", 'comment="Cover (front)"'])
            input_idx += 1

        # 2. Embed Soft Subtitles (SRT / VTT)
        sub_path = f"{base}.en.srt"
        if not os.path.isfile(sub_path):
            sub_path = f"{base}.srt"

        if self.embed_subs and os.path.isfile(sub_path):
            cmd.extend(["-i", sub_path])
            extra_maps.extend(["-map", f"{input_idx}"])
            if ext_clean in ("mp4", "m4v"):
                cmd.extend([f"-c:s:{input_idx - 1}", "mov_text"])
            elif ext_clean == "mkv":
                cmd.extend([f"-c:s:{input_idx - 1}", "srt"])
            input_idx += 1

        # 3. Embed Metadata
        if self.embed_metadata:
            if info.title:
                cmd.extend(["-metadata", f"title={info.title}"])
            if info.uploader or info.channel:
                cmd.extend(["-metadata", f"artist={info.uploader or info.channel}"])
                cmd.extend(["-metadata", f"album_artist={info.uploader or info.channel}"])
            if info.description:
                cmd.extend(["-metadata", f"comment={info.description[:500]}"])
            if info.upload_date:
                cmd.extend(["-metadata", f"date={info.upload_date}"])

        # Stream copying where possible
        if not self.embed_thumbnail or ext_clean not in ("mp3", "m4a"):
            cmd.extend(["-c", "copy"])

        cmd.extend(extra_maps)
        cmd.append(out_filepath)

        logger.info(f"[embedder] Running embedding: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if res.returncode == 0 and os.path.isfile(out_filepath):
                os.remove(info.filepath)
                os.rename(out_filepath, info.filepath)
                logger.info(f"[embedder] Successfully embedded media components into {info.filepath}")
            elif os.path.isfile(out_filepath):
                os.remove(out_filepath)
        except Exception as e:
            logger.warning(f"[embedder] Embedder execution failed: {e}")
            if os.path.isfile(out_filepath):
                os.remove(out_filepath)

        return [], info
