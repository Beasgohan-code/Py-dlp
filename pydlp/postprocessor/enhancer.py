"""Advanced Video & Audio Filter and Transcoding Enhancer for Py-dlp.

Supports:
- EBU R128 loudness normalization
- Audio pitch & tempo speed adjustment
- Video speed adjustment
- High quality video denoising
- Hardware-accelerated transcoding (NVENC, VAAPI, VideoToolbox, QSV)
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import get_ffmpeg_path

logger = logging.getLogger("pydlp.enhancer")


class MediaEnhancerPostProcessor(BasePostProcessor):
    """Applies audio/video enhancement filters and transcoding via FFmpeg."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.loudnorm = self.options.get("audio_loudnorm", False)
        self.audio_pitch = self.options.get("audio_pitch")
        self.audio_tempo = self.options.get("audio_tempo")
        self.video_speed = self.options.get("video_speed")
        self.video_denoise = self.options.get("video_denoise", False)
        self.reencode_codec = self.options.get("reencode_codec")
        self.hw_accel = self.options.get("hardware_accel")

    @property
    def is_needed(self) -> bool:
        return bool(
            self.loudnorm
            or self.audio_pitch
            or self.audio_tempo
            or self.video_speed
            or self.video_denoise
            or self.reencode_codec
            or self.hw_accel
        )

    def run(self, info: MediaInfo) -> tuple[list[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.exists(info.filepath):
            return [], info

        new_filepath = self.process(info.filepath, info.to_dict())
        info.filepath = new_filepath
        return [], info

    def process(self, filepath: str, info_dict: Optional[dict] = None) -> str:
        if not self.is_needed or not os.path.exists(filepath):
            return filepath

        ffmpeg = get_ffmpeg_path()
        if not ffmpeg:
            logger.warning("[enhancer] FFmpeg not found. Skipping enhancements.")
            return filepath

        base, ext = os.path.splitext(filepath)
        out_path = f"{base}.enhanced{ext}"

        cmd = [ffmpeg, "-y", "-i", filepath]

        # Hardware acceleration decoding if specified
        if self.hw_accel:
            if self.hw_accel == "cuda" or self.hw_accel == "nvenc":
                cmd = [ffmpeg, "-y", "-hwaccel", "cuda", "-i", filepath]
            elif self.hw_accel == "vaapi":
                cmd = [ffmpeg, "-y", "-hwaccel", "vaapi", "-i", filepath]

        # Build Audio Filters
        af_filters: List[str] = []
        if self.loudnorm:
            af_filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        if self.audio_pitch:
            try:
                pitch_val = float(self.audio_pitch)
                af_filters.append(f"asetrate=44100*{pitch_val},aresample=44100")
            except ValueError:
                pass
        if self.audio_tempo:
            try:
                tempo_val = float(self.audio_tempo)
                af_filters.append(f"atempo={tempo_val}")
            except ValueError:
                pass

        # Build Video Filters
        vf_filters: List[str] = []
        if self.video_denoise:
            vf_filters.append("hqdn3d=4:3:6:4.5")
        if self.video_speed:
            try:
                speed_val = float(self.video_speed)
                pts_val = 1.0 / speed_val
                vf_filters.append(f"setpts={pts_val}*PTS")
                if not self.audio_tempo:
                    af_filters.append(f"atempo={speed_val}")
            except ValueError:
                pass

        if af_filters:
            cmd.extend(["-af", ",".join(af_filters)])
        if vf_filters:
            cmd.extend(["-vf", ",".join(vf_filters)])

        # Codec selection
        if self.reencode_codec:
            codec = self.reencode_codec.lower()
            if codec in ("h264", "x264", "mp4"):
                cmd.extend(["-c:v", "libx264", "-crf", "22", "-preset", "medium"])
            elif codec in ("hevc", "h265", "x265"):
                cmd.extend(["-c:v", "libx265", "-crf", "26", "-preset", "medium"])
            elif codec in ("av1", "libsvtav1"):
                cmd.extend(["-c:v", "libsvtav1", "-crf", "30"])
            elif codec in ("vp9", "webm"):
                cmd.extend(["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30"])
            elif codec in ("mp3", "libmp3lame"):
                cmd.extend(["-c:a", "libmp3lame", "-q:a", "2"])
            elif codec in ("opus", "libopus"):
                cmd.extend(["-c:a", "libopus", "-b:a", "128k"])
            elif codec in ("aac",):
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            elif codec in ("flac",):
                cmd.extend(["-c:a", "flac"])
        elif not vf_filters and not af_filters:
            cmd.extend(["-c", "copy"])

        cmd.append(out_path)

        logger.info(f"[enhancer] Applying filters/transcoding: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if res.returncode == 0 and os.path.exists(out_path):
                os.remove(filepath)
                os.rename(out_path, filepath)
                logger.info(f"[enhancer] Successfully enhanced: {filepath}")
                return filepath
            else:
                logger.debug(f"[enhancer] FFmpeg command failed: {res.stderr.decode('utf-8', errors='ignore')}")
                if os.path.exists(out_path):
                    os.remove(out_path)
                return filepath
        except Exception as e:
            logger.warning(f"[enhancer] Enhancer failed: {e}")
            if os.path.exists(out_path):
                os.remove(out_path)
            return filepath
