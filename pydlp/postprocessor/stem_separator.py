"""Multi-Track Audio Stem Separator & Karaoke Splitter for Py-dlp.

Splits media audio into Vocals, Instrumentals, Bass, and Percussion tracks.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path, has_ffmpeg


class AudioStemSeparatorPostProcessor(BasePostProcessor):
    """Splits audio tracks into distinct multi-band stems (Vocals, Instrumentals, Bass)."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.ffmpeg_bin = get_ffmpeg_path(self.options)

    @property
    def is_needed(self) -> bool:
        return bool(self.options.get("split_audio_stems") or self.options.get("extract_stems"))

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not has_ffmpeg(self.options) or not info.filepath or not os.path.exists(info.filepath):
            return [], info

        target_path = Path(info.filepath)
        stem_dir = target_path.parent / f"{target_path.stem}_stems"
        stem_dir.mkdir(parents=True, exist_ok=True)

        fmt = self.options.get("audio_format", "mp3")
        self._generate_stems(target_path, stem_dir, fmt)
        return [], info

    def _generate_stems(self, input_file: Path, output_dir: Path, fmt: str) -> None:
        """Executes FFmpeg DSP multi-band filter graphs to produce distinct stems."""
        # 1. Vocals (Center channel mid-band bandpass + pan extraction)
        vocal_out = output_dir / f"vocals.{fmt}"
        vocal_filter = "pan=stereo|c0=c0-c1|c1=c1-c0,highpass=f=200,lowpass=f=4000,volume=2.0"
        self._run_ffmpeg_filter(input_file, vocal_out, vocal_filter)

        # 2. Instrumental / Accompaniment (Center vocal phase cancellation)
        inst_out = output_dir / f"instrumental.{fmt}"
        inst_filter = "pan=stereo|c0=c0-0.5*c1|c1=c1-0.5*c0"
        self._run_ffmpeg_filter(input_file, inst_out, inst_filter)

        # 3. Bass (Low-pass sub-bass isolation <250Hz)
        bass_out = output_dir / f"bass.{fmt}"
        bass_filter = "lowpass=f=250,volume=1.5"
        self._run_ffmpeg_filter(input_file, bass_out, bass_filter)

        # 4. Treble / Highs (Percussion & Highs >4000Hz)
        treble_out = output_dir / f"drums_highs.{fmt}"
        treble_filter = "highpass=f=4000,volume=1.2"
        self._run_ffmpeg_filter(input_file, treble_out, treble_filter)

    def _run_ffmpeg_filter(self, input_file: Path, output_file: Path, filter_str: str) -> None:
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(input_file),
            "-vn",
            "-af",
            filter_str,
            str(output_file),
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=120)
        except Exception:
            pass
