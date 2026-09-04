"""FFmpeg integration wrapper for media remuxing, transcoding, and stream merging."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor


def has_ffmpeg(ffmpeg_path: Optional[str] = None) -> bool:
    """Checks whether ffmpeg executable is installed and available."""
    bin_name = ffmpeg_path or "ffmpeg"
    return shutil.which(bin_name) is not None


class FFmpegPostProcessor(BasePostProcessor):
    """Executes FFmpeg commands for media processing."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.ffmpeg_bin = self.options.get("ffmpeg_location") or "ffmpeg"
        self.is_available = has_ffmpeg(self.ffmpeg_bin)

    def _run_cmd(self, args: List[str]) -> None:
        cmd = [self.ffmpeg_bin, "-y", "-v", "error", "-stats"] + args
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if p.returncode != 0:
                raise PostProcessingError(f"FFmpeg error ({p.returncode}): {p.stderr.strip()}")
        except FileNotFoundError:
            raise PostProcessingError(f"FFmpeg executable not found at '{self.ffmpeg_bin}'")

    def merge_video_audio(
        self, video_file: str, audio_file: str, output_file: str, format_container: str = "mp4"
    ) -> None:
        """Merges separate video and audio files into a single container without re-encoding."""
        args = [
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "copy",
            output_file,
        ]
        self._run_cmd(args)

    def extract_audio(
        self,
        input_file: str,
        output_file: str,
        audio_format: str = "mp3",
        audio_quality: str = "192k",
    ) -> None:
        """Transcodes media to pure audio track."""
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "m4a": "aac",
            "opus": "libopus",
            "flac": "flac",
            "wav": "pcm_s16le",
        }
        codec = codec_map.get(audio_format.lower(), "copy")
        args = [
            "-i", input_file,
            "-vn",
            "-c:a", codec,
        ]
        if codec != "copy" and audio_format.lower() in ("mp3", "aac", "m4a", "opus"):
            args.extend(["-b:a", audio_quality])
        args.append(output_file)
        self._run_cmd(args)

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        """Auto-dispatches post-processing tasks based on configuration."""
        files_to_delete: List[str] = []
        filepath = info.filepath or info.filename
        if not filepath or not os.path.exists(filepath):
            return files_to_delete, info

        # Audio extraction option
        if self.options.get("extract_audio", False):
            if not self.is_available:
                return files_to_delete, info
            target_format = self.options.get("audio_format", "mp3")
            quality = self.options.get("audio_quality", "192k")

            base_stem, _ = os.path.splitext(filepath)
            out_audio = f"{base_stem}.{target_format}"

            if out_audio != filepath:
                self.extract_audio(filepath, out_audio, audio_format=target_format, audio_quality=quality)
                if not self.options.get("keep_video", False):
                    files_to_delete.append(filepath)
                info.filepath = out_audio
                info.filename = os.path.basename(out_audio)
                info.ext = target_format

        return files_to_delete, info
