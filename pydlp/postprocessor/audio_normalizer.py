"""Audio loudness normalizer (EBU R128 standard)."""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import has_ffmpeg


class AudioNormalizerPostProcessor(BasePostProcessor):
    """Applies EBU R128 loudness normalization to ensure consistent audio levels."""

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        if not self.options.get("normalize_audio", False) or not has_ffmpeg(self.options.get("ffmpeg_location")):
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath or not os.path.exists(filepath):
            return files_to_delete, info

        target_lufs = self.options.get("target_lufs", -14.0)
        base_stem, ext = os.path.splitext(filepath)
        norm_out = f"{base_stem}.norm{ext}"
        ffmpeg_bin = self.options.get("ffmpeg_location") or "ffmpeg"

        # Apply loudnorm filter
        filter_str = f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11"
        is_audio = ext.lower() in (".mp3", ".m4a", ".aac", ".opus", ".flac", ".wav", ".ogg")

        if is_audio:
            cmd = [ffmpeg_bin, "-y", "-i", filepath, "-af", filter_str, norm_out]
        else:
            cmd = [ffmpeg_bin, "-y", "-i", filepath, "-c:v", "copy", "-af", filter_str, norm_out]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(norm_out):
                files_to_delete.append(filepath)
                os.replace(norm_out, filepath)
        except Exception:
            pass

        return files_to_delete, info
