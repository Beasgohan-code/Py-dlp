"""Time-range trimmer and lossless stream cutter."""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.types import MediaInfo
from pydlp.core.utils import parse_duration
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import has_ffmpeg


def parse_time_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parses range strings like '*01:00-03:30' or '60-210' into (start_seconds, end_seconds)."""
    s = range_str.lstrip("*").strip()
    if "-" not in s:
        return parse_duration(s), None
    start_str, end_str = s.split("-", 1)
    return parse_duration(start_str), parse_duration(end_str)


class TimeRangeCutterPostProcessor(BasePostProcessor):
    """Trims media files to specified time ranges."""

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        time_range = self.options.get("time_range") or self.options.get("download_sections")
        if not time_range or not has_ffmpeg(self.options.get("ffmpeg_location")):
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath or not os.path.exists(filepath):
            return files_to_delete, info

        start_sec, end_sec = parse_time_range(time_range)
        if start_sec is None and end_sec is None:
            return files_to_delete, info

        base_stem, ext = os.path.splitext(filepath)
        trimmed_out = f"{base_stem}.trimmed{ext}"
        ffmpeg_bin = self.options.get("ffmpeg_location") or "ffmpeg"

        cmd = [ffmpeg_bin, "-y"]
        if start_sec is not None:
            cmd.extend(["-ss", str(start_sec)])
        if end_sec is not None:
            cmd.extend(["-to", str(end_sec)])
        cmd.extend(["-i", filepath, "-c", "copy", trimmed_out])

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(trimmed_out):
                files_to_delete.append(filepath)
                os.replace(trimmed_out, filepath)
                if start_sec is not None and end_sec is not None:
                    info.duration = end_sec - start_sec
        except Exception:
            pass

        return files_to_delete, info
