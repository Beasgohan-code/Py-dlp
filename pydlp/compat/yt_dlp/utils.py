"""yt-dlp compatibility utils module implemented using pure Python stdlib."""

from __future__ import annotations

import base64
import datetime
import html
import json
import mimetypes
import os
import re
import urllib.parse
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydlp.core.exceptions import ExtractorError
from pydlp.core.utils import (
    clean_html,
    determine_ext,
    float_or_none,
    format_bytes,
    format_seconds,
    int_or_none,
    parse_duration,
    parse_filesize,
    parse_iso8601,
    parse_m3u8_attributes,
    str_or_none,
    try_get,
    unescape_html,
    urljoin,
)

# Common utility aliases matching yt_dlp.utils
unescapeHTML = unescape_html
ExtractorError = ExtractorError


def str_to_int(val: Any) -> Optional[int]:
    return int_or_none(val)


def url_or_none(url: Any) -> Optional[str]:
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if url.startswith(("http://", "https://", "//", "ftp://")):
        return url
    return None


def js_to_json(code: str) -> str:
    """Convert a JavaScript object literal into valid JSON."""
    if not code:
        return ""
    # Strip comments
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\r\n]*", "", code)
    # Quote unquoted keys: { key: "val" } -> { "key": "val" }
    code = re.sub(r'(?<=[{,])\s*([a-zA-Z0-9_$]+)\s*:', r' "\1":', code)
    # Replace single quotes with double quotes
    code = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', code)
    # Strip trailing commas
    code = re.sub(r",\s*([\]}])", r"\1", code)
    return code


def traverse_obj(obj: Any, *paths: Any, default: Any = None, casesense: bool = True) -> Any:
    """Traverse a nested dict/list structure safely (yt-dlp traverse_obj)."""
    if obj is None:
        return default

    for path in paths:
        curr = obj
        if not isinstance(path, (list, tuple)):
            path = [path]

        found = True
        for key in path:
            if isinstance(curr, dict):
                if casesense:
                    if key in curr:
                        curr = curr[key]
                    else:
                        found = False
                        break
                else:
                    k_lower = str(key).lower()
                    matched = False
                    for k, v in curr.items():
                        if str(k).lower() == k_lower:
                            curr = v
                            matched = True
                            break
                    if not matched:
                        found = False
                        break
            elif isinstance(curr, (list, tuple)):
                if isinstance(key, int) and -len(curr) <= key < len(curr):
                    curr = curr[key]
                else:
                    found = False
                    break
            else:
                found = False
                break

        if found and curr is not None:
            return curr

    return default


def unified_strdate(date_str: Optional[str], day_first: bool = True) -> Optional[str]:
    """Parse date string into YYYYMMDD format."""
    if not date_str:
        return None
    date_str = date_str.strip()
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", date_str)
    if m:
        year, month, day = m.groups()
        return f"{int(year):04d}{int(month):02d}{int(day):02d}"
    return None


def unified_timestamp(date_str: Optional[str]) -> Optional[int]:
    """Parse date string into Unix timestamp."""
    return parse_iso8601(date_str)


def mimetype2ext(mimetype: Optional[str]) -> Optional[str]:
    if not mimetype:
        return None
    mimetype = mimetype.split(";")[0].strip().lower()
    mapping = {
        "video/mp4": "mp4",
        "video/webm": "webm",
        "video/x-flv": "flv",
        "video/ogg": "ogv",
        "video/quicktime": "mov",
        "video/x-matroska": "mkv",
        "audio/mp4": "m4a",
        "audio/mpeg": "mp3",
        "audio/ogg": "ogg",
        "audio/webm": "webm",
        "audio/x-wav": "wav",
        "audio/flac": "flac",
        "audio/aac": "aac",
        "application/vnd.apple.mpegurl": "m3u8",
        "application/x-mpegurl": "m3u8",
        "application/dash+xml": "mpd",
    }
    return mapping.get(mimetype, mimetypes.guess_extension(mimetype, strict=False) or None)


def format_field(obj: Any, field: str, fmt: str = "%s", default: Any = None) -> Any:
    if obj is None:
        return default
    val = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
    if val is None or val == "":
        return default
    return fmt % val


def remove_start(s: Optional[str], start: str) -> Optional[str]:
    if s is not None and s.startswith(start):
        return s[len(start):]
    return s


def remove_end(s: Optional[str], end: str) -> Optional[str]:
    if s is not None and s.endswith(end):
        return s[:-len(end)]
    return s


def sanitize_filename(filename: str, restricted: bool = False) -> str:
    """Sanitize filename removing problematic filesystem characters."""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    if restricted:
        filename = re.sub(r"[^\w\-.]", "_", filename)
    return filename
