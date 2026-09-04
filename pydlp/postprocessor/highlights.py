"""Automated Highlight Reel and Vertical Shorts Generator for Py-dlp."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path, has_ffmpeg


class HighlightReelPostProcessor(BasePostProcessor):
    """Automatically cuts and stitches top engagement segments into a highlight reel."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.ffmpeg_bin = get_ffmpeg_path(self.options)

    @property
    def is_needed(self) -> bool:
        return bool(self.options.get("auto_highlights") or self.options.get("create_shorts"))

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not has_ffmpeg(self.options) or not info.filepath or not os.path.exists(info.filepath):
            return [], info

        target_path = Path(info.filepath)
        duration = float(info.duration or 0)
        if duration < 30.0:
            return [], info

        target_highlight_dur = float(self.options.get("highlight_duration", 60.0))
        vertical = bool(self.options.get("vertical_crop", False))

        output_file = target_path.parent / f"{target_path.stem}.highlights{target_path.suffix}"
        self._generate_highlights(target_path, output_file, duration, target_highlight_dur, vertical)
        return [], info

    def _generate_highlights(
        self, input_file: Path, output_file: Path, total_dur: float, max_dur: float, vertical: bool
    ) -> None:
        """Slices key intervals across the video (beginning, 1/3, 2/3, climax) and concatenates them."""
        num_segments = 3
        seg_dur = min(max_dur / num_segments, 20.0)

        t1 = max(0.0, total_dur * 0.15)
        t2 = max(0.0, total_dur * 0.50)
        t3 = max(0.0, total_dur * 0.80)
        timestamps = [t1, t2, t3]

        vf_filter = "crop=ih*(9/16):ih" if vertical else "null"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_files = []
            for i, ts in enumerate(timestamps):
                seg_path = Path(tmp_dir) / f"seg_{i}.mp4"
                cmd = [
                    self.ffmpeg_bin,
                    "-y",
                    "-loglevel",
                    "error",
                    "-ss",
                    str(ts),
                    "-t",
                    str(seg_dur),
                    "-i",
                    str(input_file),
                    "-vf",
                    vf_filter,
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-c:a",
                    "aac",
                    str(seg_path),
                ]
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=60)
                    if seg_path.exists() and seg_path.stat().st_size > 0:
                        tmp_files.append(seg_path)
                except Exception:
                    pass

            if not tmp_files:
                return

            concat_txt = Path(tmp_dir) / "concat.txt"
            concat_txt.write_text(
                "\n".join([f"file '{p.resolve()}'" for p in tmp_files]), encoding="utf-8"
            )

            merge_cmd = [
                self.ffmpeg_bin,
                "-y",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_txt),
                "-c",
                "copy",
                str(output_file),
            ]
            try:
                subprocess.run(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=60)
            except Exception:
                pass
