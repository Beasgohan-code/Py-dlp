"""AI Speech-to-Text Transcription & Subtitle Generator for Py-dlp.

Generates .srt and .vtt subtitle tracks automatically from media audio tracks using Whisper/AI models.
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo, MediaSubtitle
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path

logger = logging.getLogger("pydlp.whisper_subtitles")


class AISubtitleGeneratorPostProcessor(BasePostProcessor):
    """Generates local subtitle files via speech-to-text models."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.enabled = self.options.get("ai_transcribe", False)
        self.model = self.options.get("ai_transcribe_model", "base")

    @property
    def is_needed(self) -> bool:
        return self.enabled

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.isfile(info.filepath):
            return [], info

        base, _ = os.path.splitext(info.filepath)
        srt_path = f"{base}.ai.srt"

        # Check if Whisper CLI or Python whisper is available
        whisper_bin = self.options.get("whisper_path", "whisper")
        try:
            cmd = [whisper_bin, info.filepath, "--model", self.model, "--output_format", "srt", "--output_dir", os.path.dirname(info.filepath) or "."]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if res.returncode == 0:
                logger.info(f"[ai_transcribe] Generated subtitle: {srt_path}")
                sub_track = MediaSubtitle(ext="srt", url=srt_path, name=f"AI Whisper ({self.model})", language="auto")
                info.subtitles.setdefault("auto", []).append(sub_track)
        except Exception as e:
            logger.debug(f"[ai_transcribe] Whisper execution skipped: {e}")

        return [], info
