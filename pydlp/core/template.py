"""Template engine for formatting output filenames and paths in Py-dlp."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional, Union

from pydlp.core.types import MediaInfo
from pydlp.core.utils import sanitize_filename

_TEMPLATE_FIELD_RE = re.compile(
    r"%\((?P<key>[a-zA-Z0-9_]+)(?::(?P<default>[^)]*))?\)(?P<conv>[0-9]*[a-zA-Z])?"
)


class TemplateFormatter:
    """Formats output filename templates following yt-dlp conventions."""

    def __init__(self, template: str = "%(title)s [%(id)s].%(ext)s", restricted: bool = False):
        self.template = template
        self.restricted = restricted
        self._autonumber = 0

    def format(
        self,
        info: Union[str, MediaInfo, Dict[str, Any]],
        ext_or_info: Optional[Union[str, MediaInfo, Dict[str, Any]]] = None,
        autonumber: Optional[int] = None,
    ) -> str:
        """Evaluates template against media info dictionary/dataclass."""
        active_template = self.template

        if isinstance(info, str):
            active_template = info
            info_target = ext_or_info or {}
            ext = None
        else:
            info_target = info
            ext = ext_or_info if isinstance(ext_or_info, str) else None

        if isinstance(info_target, MediaInfo):
            data = info_target.to_dict()
        else:
            data = dict(info_target)

        if ext:
            data["ext"] = ext
        elif not data.get("ext"):
            data["ext"] = "mp4"

        if autonumber is not None:
            data["autonumber"] = autonumber
        else:
            self._autonumber += 1
            data["autonumber"] = self._autonumber

        # Fill common default fallbacks
        data.setdefault("id", "unknown_id")
        data.setdefault("title", "untitled")
        data.setdefault("extractor", "generic")
        data.setdefault("uploader", "unknown_uploader")
        data.setdefault("upload_date", "NA")
        data.setdefault("duration", "NA")
        data.setdefault("playlist_title", "NA")
        data.setdefault("playlist_index", 1)

        def repl(match: re.Match) -> str:
            key = match.group("key")
            default_val = match.group("default") or "NA"
            conv = match.group("conv") or "s"

            val = data.get(key)
            if val is None:
                val = default_val

            # Format conversion
            try:
                if conv.endswith("d") or conv.endswith("i"):
                    formatted_val = f"%{conv}" % int(val)
                elif conv.endswith("f"):
                    formatted_val = f"%{conv}" % float(val)
                else:
                    formatted_val = f"%{conv}" % str(val)
            except Exception:
                formatted_val = str(val)

            return formatted_val

        rendered = _TEMPLATE_FIELD_RE.sub(repl, active_template)

        # Split path segments to sanitize directories and filename separately
        parts = rendered.split(os.sep)
        sanitized_parts = []
        for i, part in enumerate(parts):
            # Also handle forward slashes if on Windows
            subparts = part.split("/")
            sanitized_subparts = [
                sanitize_filename(sp, restricted=self.restricted) if sp else ""
                for sp in subparts
            ]
            sanitized_parts.append("/".join(sanitized_subparts))

        result_path = os.sep.join(sanitized_parts)
        # Normalize
        return os.path.normpath(result_path)
