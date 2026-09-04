"""Intelligent format selection and filtering engine matching yt-dlp syntax."""

from __future__ import annotations

import operator
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydlp.core.exceptions import FormatNotAvailableError
from pydlp.core.types import MediaFormat, MediaInfo

_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne,
    "=": operator.eq,
    "==": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
    "^=": lambda a, b: str(a).startswith(str(b)),
    "$=": lambda a, b: str(a).endswith(str(b)),
    "*=": lambda a, b: str(b) in str(a),
}

_OP_PATTERN = re.compile(r"([a-zA-Z0-9_]+)\s*(<=|>=|!=|==|=|<|>|\^=|\$=|\*=)\s*([^\]]+)")


class FormatFilter:
    """Represents a single format condition filter like [height<=1080]."""

    def __init__(self, key: str, op: str, value: str):
        self.key = key.lower()
        self.op_str = op
        self.op_fn = _OPERATORS.get(op, operator.eq)
        self.raw_value = value.strip("'\"")

        # Infer typed value
        try:
            self.value: Any = int(self.raw_value)
        except ValueError:
            try:
                self.value = float(self.raw_value)
            except ValueError:
                self.value = self.raw_value.lower()

    def matches(self, fmt: MediaFormat) -> bool:
        fmt_dict = fmt.to_dict()
        val = fmt_dict.get(self.key)
        if val is None:
            if self.key == "res" or self.key == "resolution":
                val = fmt.height or 0
            elif self.key == "fps":
                val = fmt.fps or 0
            elif self.key == "ext":
                val = fmt.ext
            elif self.key == "vcodec":
                val = fmt.vcodec or "none"
            elif self.key == "acodec":
                val = fmt.acodec or "none"
            elif self.key == "tbr":
                val = fmt.get_effective_bitrate()
            else:
                return False

        if isinstance(self.value, (int, float)) and isinstance(val, (int, float)):
            try:
                return self.op_fn(float(val), float(self.value))
            except Exception:
                return False
        elif isinstance(self.value, str):
            return self.op_fn(str(val).lower(), str(self.value).lower())

        return False


def sort_formats(formats: List[MediaFormat]) -> List[MediaFormat]:
    """Sorts formats from worst to best based on resolution, fps, bitrate, and preference."""

    def format_key(f: MediaFormat) -> Tuple[int, int, float, float, int]:
        pref = f.preference if f.preference is not None else 0
        height = f.height or 0
        width = f.width or 0
        resolution_score = height * (width or (height * 16 // 9))
        fps = f.fps or 0.0
        bitrate = f.get_effective_bitrate()
        has_both = 1 if (f.has_video and f.has_audio) else 0
        return (pref, has_both, resolution_score, fps, int(bitrate))

    return sorted(formats, key=format_key)


class FormatSelector:
    """Parses format specifications and selects appropriate MediaFormat instances."""

    def __init__(self, format_spec: Optional[str] = None):
        self.format_spec = format_spec or "bestvideo+bestaudio/best"

    def select_formats(self, info: Union[MediaInfo, Dict[str, Any]]) -> List[MediaFormat]:
        """Resolves the format specification against the available formats."""
        if isinstance(info, MediaInfo):
            formats = list(info.formats)
        else:
            formats = [MediaFormat.from_dict(f) for f in info.get("formats", [])]

        if not formats:
            # If no formats exist but a direct media URL is present
            direct_url = getattr(info, "url", None) or (info.get("url") if isinstance(info, dict) else None)
            if direct_url:
                ext = getattr(info, "ext", None) or (info.get("ext") if isinstance(info, dict) else "mp4")
                return [MediaFormat(format_id="direct", url=direct_url, ext=ext)]
            return []

        # Sort formats ascending (worst to best)
        sorted_fmts = sort_formats(formats)

        # Handle 'all' selector
        if self.format_spec.strip().lower() == "all":
            return sorted_fmts

        # Fallback chain separated by '/' or ','
        spec_alternatives = [s.strip() for s in self.format_spec.split("/") if s.strip()]

        for alt in spec_alternatives:
            selected = self._evaluate_alternative(alt, sorted_fmts)
            if selected:
                return selected

        # If nothing matched the spec, fallback to absolute best available
        if sorted_fmts:
            return [sorted_fmts[-1]]

        raise FormatNotAvailableError(f"No suitable format found matching '{self.format_spec}'")

    def _evaluate_alternative(
        self, spec: str, formats: List[MediaFormat]
    ) -> Optional[List[MediaFormat]]:
        """Evaluates a single selector alternative (e.g., 'bestvideo+bestaudio' or 'best[height<=720]')."""
        if "+" in spec:
            parts = [p.strip() for p in spec.split("+")]
            picked = []
            for part in parts:
                f = self._select_single(part, formats)
                if not f:
                    return None
                picked.append(f)
            return picked
        else:
            f = self._select_single(spec, formats)
            return [f] if f else None

    def _select_single(self, expr: str, formats: List[MediaFormat]) -> Optional[MediaFormat]:
        """Selects a single format according to an expression like 'bestvideo[ext=mp4]' or '137'."""
        expr = expr.strip()
        if not expr:
            return formats[-1] if formats else None

        # Exact format ID match first
        for f in formats:
            if f.format_id.lower() == expr.lower():
                return f

        # Parse filter brackets [key=val]
        filters: List[FormatFilter] = []
        base_target = expr
        bracket_matches = re.findall(r"\[([^\]]+)\]", expr)
        if bracket_matches:
            base_target = re.sub(r"\[[^\]]+\]", "", expr).strip()
            for bm in bracket_matches:
                m = _OP_PATTERN.match(bm)
                if m:
                    filters.append(FormatFilter(m.group(1), m.group(2), m.group(3)))

        # Candidate pool filtering
        candidates = formats
        for flt in filters:
            candidates = [f for f in candidates if flt.matches(f)]
            if not candidates:
                return None

        target = base_target.lower()
        if target in ("best", "b", ""):
            # Prefers complete video+audio streams, else best
            complete = [f for f in candidates if f.has_video and f.has_audio]
            if complete:
                return complete[-1]
            return candidates[-1]

        elif target in ("worst", "w"):
            complete = [f for f in candidates if f.has_video and f.has_audio]
            if complete:
                return complete[0]
            return candidates[0]

        elif target in ("bestvideo", "bv"):
            video_only = [f for f in candidates if f.has_video and not f.has_audio]
            if video_only:
                return video_only[-1]
            videos = [f for f in candidates if f.has_video]
            return videos[-1] if videos else None

        elif target in ("worstvideo", "wv"):
            video_only = [f for f in candidates if f.has_video and not f.has_audio]
            if video_only:
                return video_only[0]
            videos = [f for f in candidates if f.has_video]
            return videos[0] if videos else None

        elif target in ("bestaudio", "ba"):
            audio_only = [f for f in candidates if f.acodec_only]
            if audio_only:
                return audio_only[-1]
            audios = [f for f in candidates if f.has_audio]
            return audios[-1] if audios else None

        elif target in ("worstaudio", "wa"):
            audio_only = [f for f in candidates if f.acodec_only]
            if audio_only:
                return audio_only[0]
            audios = [f for f in candidates if f.has_audio]
            return audios[0] if audios else None

        else:
            # If target matches an extension (e.g., 'mp4', 'm4a', 'webm', 'mp3')
            by_ext = [f for f in candidates if f.ext.lower() == target]
            if by_ext:
                return by_ext[-1]

            # Format ID search inside candidates
            for f in candidates:
                if f.format_id.lower() == target:
                    return f

        return candidates[-1] if candidates else None
