"""Utility functions and helpers for Py-dlp."""

from __future__ import annotations

import datetime
import html
import os
import re
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

T = TypeVar("T")

# Windows reserved device names
_WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

# Illegal characters on major OS (Windows, macOS, Linux)
_ILLEGAL_CHARS_RE = re.compile(r'[\x00-\x1f\x7f/\\:*\?"<>|]')
_RESTRICTED_CHARS_RE = re.compile(r"[^a-zA-Z0-9_.-]")


def sanitize_filename(
    name: str,
    restricted: bool = False,
    is_id: bool = False,
    max_length: int = 240,
) -> str:
    """Sanitizes a string to be safely used as a filename on any OS."""
    if not name:
        return "untitled"

    # Normalize unicode
    name = unicodedata.normalize("NFKC", str(name))

    # Replace forbidden path separators and illegal characters with safe alternates
    name = name.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    name = _ILLEGAL_CHARS_RE.sub("_", name)

    if restricted:
        name = _RESTRICTED_CHARS_RE.sub("_", name)

    # Strip leading/trailing whitespaces, dots, underscores
    name = name.strip(" ._\t")

    # Check Windows reserved names
    base_stem = name.split(".")[0].upper()
    if base_stem in _WINDOWS_RESERVED_NAMES:
        name = f"_{name}"

    if not name:
        name = "untitled"

    # Truncate length safely taking UTF-8 byte boundary into account
    encoded = name.encode("utf-8")
    if len(encoded) > max_length:
        truncated = encoded[:max_length].decode("utf-8", "ignore")
        name = truncated.rstrip(" ._\t") or "untitled"

    return name


def format_bytes(bytes_count: Optional[Union[int, float]]) -> str:
    """Formats byte counts into human-readable strings (e.g. 14.50MiB)."""
    if bytes_count is None or bytes_count < 0:
        return "N/A"
    bytes_float = float(bytes_count)
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    for unit in units:
        if bytes_float < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(bytes_float)}B"
            return f"{bytes_float:.2f}{unit}"
        bytes_float /= 1024.0
    return f"{bytes_float:.2f}PiB"


def format_speed(bytes_per_sec: Optional[Union[int, float]]) -> str:
    """Formats transfer speed into human-readable string (e.g. 3.20MiB/s)."""
    if bytes_per_sec is None or bytes_per_sec < 0:
        return "N/A"
    return f"{format_bytes(bytes_per_sec)}/s"


def format_seconds(seconds: Optional[Union[int, float]]) -> str:
    """Formats seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "--:--"
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def parse_duration(duration_str: Optional[Union[str, int, float]]) -> Optional[float]:
    """Parses various duration string formats into seconds as float."""
    if duration_str is None:
        return None
    if isinstance(duration_str, (int, float)):
        return float(duration_str)

    s = str(duration_str).strip()
    if not s:
        return None

    # Handle ISO 8601 duration: PT1H23M45S or PT45S
    iso_match = re.match(
        r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$",
        s,
        re.IGNORECASE,
    )
    if iso_match:
        parts = iso_match.groupdict()
        days = float(parts.get("days") or 0)
        hours = float(parts.get("hours") or 0)
        minutes = float(parts.get("minutes") or 0)
        seconds = float(parts.get("seconds") or 0)
        return days * 86400 + hours * 3600 + minutes * 60 + seconds

    # Handle numeric string
    try:
        return float(s)
    except ValueError:
        pass

    # Handle HH:MM:SS or MM:SS
    parts = s.split(":")
    try:
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 1:
            return float(parts[0])
    except ValueError:
        pass

    return None


def parse_filesize(size_str: Optional[str]) -> Optional[int]:
    """Parses human-readable file size strings into integer bytes."""
    if not size_str:
        return None
    s = size_str.strip().upper()
    match = re.match(r"^([0-9.]+)\s*([KMGTPE]?I?B?)$", s)
    if not match:
        return None
    val, unit = match.groups()
    try:
        num = float(val)
    except ValueError:
        return None

    multipliers = {
        "": 1,
        "B": 1,
        "K": 1024,
        "KB": 1000,
        "KIB": 1024,
        "M": 1024**2,
        "MB": 1000**2,
        "MIB": 1024**2,
        "G": 1024**3,
        "GB": 1000**3,
        "GIB": 1024**3,
        "T": 1024**4,
        "TB": 1000**4,
        "TIB": 1024**4,
    }
    return int(num * multipliers.get(unit, 1))


def clean_html(raw_html: Optional[str]) -> str:
    """Strips HTML tags and decodes entities."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def unescape_html(s: Optional[str]) -> str:
    """Unescapes HTML entities."""
    if not s:
        return ""
    return html.unescape(s)


def parse_iso8601(date_str: Optional[str]) -> Tuple[Optional[str], Optional[int]]:
    """Parses ISO8601 timestamp string into (YYYYMMDD, unix_timestamp)."""
    if not date_str:
        return None, None
    s = str(date_str).strip()
    # Normalize Z to +00:00
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(s)
        upload_date = dt.strftime("%Y%m%d")
        ts = int(dt.timestamp())
        return upload_date, ts
    except Exception:
        # Try regex YYYY-MM-DD
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            return f"{m.group(1)}{m.group(2)}{m.group(3)}", None
    return None, None


def determine_ext(url: Optional[str], default_ext: str = "mp4") -> str:
    """Extracts a clean media file extension from a URL."""
    if not url:
        return default_ext
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    _, ext = os.path.splitext(path)
    if ext:
        clean = ext.lstrip(".").lower().split("?")[0]
        if clean in (
            "mp4", "m4v", "mkv", "webm", "flv", "avi", "mov", "ts", "m3u8",
            "mpd", "mp3", "m4a", "aac", "ogg", "opus", "flac", "wav", "vtt",
            "srt", "ass", "jpg", "jpeg", "png", "webp",
        ):
            return clean
    return default_ext


def int_or_none(val: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely converts value to int or default/None."""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def float_or_none(val: Any, default: Optional[float] = None) -> Optional[float]:
    """Safely converts value to float or default/None."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def str_or_none(val: Any, default: Optional[str] = None) -> Optional[str]:
    """Safely converts value to string or default/None."""
    if val is None:
        return default
    s = str(val).strip()
    return s if s else default


def try_get(
    src: Any,
    getter: Union[Callable[[Any], T], Sequence[Callable[[Any], T]]],
    expected_type: Optional[type] = None,
) -> Optional[T]:
    """Safely navigates nested data structures without throwing KeyError/IndexError/TypeError."""
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get_fn in getter:
        try:
            val = get_fn(src)
        except (KeyError, IndexError, TypeError, AttributeError):
            continue
        if val is not None:
            if expected_type is None or isinstance(val, expected_type):
                return val
    return None


def parse_m3u8_attributes(attrib_line: str) -> Dict[str, str]:
    """Parses an M3U8 tag attribute string like BANDWIDTH=1280000,RESOLUTION=1280x720,CODECS="avc1..."."""
    res = {}
    pattern = re.compile(r'([A-Z0-9\-]+)=(?:"([^"]*)"|([^,]*))')
    for m in pattern.finditer(attrib_line):
        key = m.group(1)
        val = m.group(2) if m.group(2) is not None else m.group(3)
        res[key] = val
    return res


def urljoin(base: str, url: str) -> str:
    """Joins base URL and relative URL cleanly."""
    return urllib.parse.urljoin(base, url)


def ordered_set(items: Iterable[T]) -> List[T]:
    """Returns unique items maintaining initial insertion order."""
    seen = set()
    res = []
    for x in items:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res
