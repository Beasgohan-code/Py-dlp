"""Audio DSP, Vocal Remover (Karaoke), and Bass Boost post-processor for Py-dlp."""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path

logger = logging.getLogger("pydlp.audio_dsp")


class AudioDSPPostProcessor(BasePostProcessor):
    """Applies advanced audio DSP filters (vocal remover, bass boost, reverb)."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.vocal_removal = self.options.get("vocal_removal", False)
        self.bass_boost = self.options.get("audio_bass_boost")
        self.audio_reverb = self.options.get("audio_reverb", False)

    @property
    def is_needed(self) -> bool:
        return bool(self.vocal_removal or self.bass_boost or self.audio_reverb)

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.isfile(info.filepath):
            return [], info

        ffmpeg = get_ffmpeg_path()
        if not ffmpeg:
            return [], info

        base, ext = os.path.splitext(info.filepath)
        out_path = f"{base}.dsp{ext}"

        filters = []
        if self.vocal_removal:
            # Vocal removal via out-of-phase stereo cancellation
            filters.append("pan=stereo|c0=c0-c1|c1=c1-c0")
        if self.bass_boost:
            try:
                gain = float(self.bass_boost)
                filters.append(f"bass=g={gain}:f=110:w=0.6")
            except ValueError:
                filters.append("bass=g=8:f=110:w=0.6")
        if self.audio_reverb:
            filters.append("aecho=0.8:0.88:60:0.4")

        cmd = [ffmpeg, "-y", "-i", info.filepath, "-af", ",".join(filters), "-c:v", "copy", out_path]
        logger.info(f"[audio_dsp] Running DSP filters: {' '.join(cmd)}")

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if res.returncode == 0 and os.path.exists(out_path):
                os.remove(info.filepath)
                os.rename(out_path, info.filepath)
                logger.info(f"[audio_dsp] Successfully processed DSP for: {info.filepath}")
            elif os.path.exists(out_path):
                os.remove(out_path)
        except Exception as e:
            logger.warning(f"[audio_dsp] DSP error: {e}")
            if os.path.exists(out_path):
                os.remove(out_path)

        return [], info
