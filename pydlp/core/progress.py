"""Progress reporting, terminal formatting, and event dispatchers for Py-dlp."""

from __future__ import annotations

import collections
import os
import sys
import time
from typing import Callable, Deque, Dict, List, Optional, Tuple, Union

from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.core.utils import format_bytes, format_seconds, format_speed


class TerminalColors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_GREEN = "\033[92m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"


def colorize(text: str, color_code: str, enable: bool = True) -> str:
    """Wraps text in ANSI color codes if enabled."""
    if not enable or not color_code:
        return text
    return f"{color_code}{text}{TerminalColors.RESET}"


class ProgressHookDispatcher:
    """Manages and invokes progress event callbacks."""

    def __init__(self):
        self._hooks: List[Callable[[DownloadProgress], None]] = []

    def add_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        if hook not in self._hooks:
            self._hooks.append(hook)

    def remove_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        if hook in self._hooks:
            self._hooks.remove(hook)

    def dispatch(self, progress: DownloadProgress) -> None:
        for hook in self._hooks:
            try:
                hook(progress)
            except Exception:
                pass


class SpeedCalculator:
    """Calculates smoothed download speed and estimated time of arrival."""

    def __init__(self, window_size: int = 8):
        self.window_size = window_size
        self._samples: Deque[Tuple[float, int]] = collections.deque(maxlen=window_size)

    def update(self, downloaded_bytes: int) -> Tuple[Optional[float], Optional[float]]:
        """Updates sample and returns (speed_bytes_sec, eta_sec)."""
        now = time.monotonic()
        self._samples.append((now, downloaded_bytes))

        if len(self._samples) < 2:
            return None, None

        t_first, b_first = self._samples[0]
        t_last, b_last = self._samples[-1]

        dt = t_last - t_first
        db = b_last - b_first

        if dt <= 0 or db <= 0:
            return None, None

        speed = db / dt
        return speed, None


class ConsoleProgressBar:
    """Render a yt-dlp style rich console progress bar in real-time."""

    def __init__(self, enable_colors: bool = True, is_tty: Optional[bool] = None):
        self.enable_colors = enable_colors
        self.is_tty = is_tty if is_tty is not None else sys.stdout.isatty()
        self.last_render_time = 0.0

    def __call__(self, progress: DownloadProgress) -> None:
        now = time.monotonic()
        if progress.status == "downloading":
            if (now - self.last_render_time) < 0.1:
                return
            self.last_render_time = now

            pct = f"{progress.percentage:5.1f}%"
            downloaded = format_bytes(progress.downloaded_bytes)
            total = format_bytes(progress.total_bytes or progress.total_bytes_estimate)
            speed = format_speed(progress.speed)
            eta = format_seconds(progress.eta)

            tag = colorize("[download]", TerminalColors.BRIGHT_CYAN, self.enable_colors)
            pct_colored = colorize(pct, TerminalColors.BRIGHT_GREEN, self.enable_colors)
            frag = ""
            if progress.fragment_count and progress.fragment_index is not None:
                frag = f" (frag {progress.fragment_index}/{progress.fragment_count})"

            line = f"\r{tag} {pct_colored} of {total} at {speed} ETA {eta}{frag}   "
            sys.stdout.write(line)
            sys.stdout.flush()

        elif progress.status == "finished":
            tag = colorize("[download]", TerminalColors.BRIGHT_CYAN, self.enable_colors)
            msg = colorize("100%", TerminalColors.BRIGHT_GREEN, self.enable_colors)
            total = format_bytes(progress.downloaded_bytes)
            elapsed = format_seconds(progress.elapsed)
            sys.stdout.write(f"\r{tag} {msg} of {total} in {elapsed}                                        \n")
            sys.stdout.flush()

        elif progress.status == "error":
            tag = colorize("[error]", TerminalColors.RED, self.enable_colors)
            err_msg = progress.error or "Unknown download error"
            sys.stdout.write(f"\n{tag} {err_msg}\n")
            sys.stdout.flush()


def format_table(headers: List[str], rows: List[List[str]], alignments: Optional[List[str]] = None) -> str:
    """Formats a clean tabular representation with auto-sized column widths."""
    if not rows:
        return ""
    col_count = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(min(len(row), col_count)):
            widths[i] = max(widths[i], len(str(row[i])))

    if not alignments:
        alignments = ["<"] * col_count

    lines = []
    # Header
    header_cells = [
        f"{headers[i]:{alignments[i]}{widths[i]}}" for i in range(col_count)
    ]
    lines.append(" ".join(header_cells))
    # Separator
    lines.append(" ".join(["-" * w for w in widths]))
    # Rows
    for row in rows:
        cells = []
        for i in range(col_count):
            val = str(row[i]) if i < len(row) else ""
            cells.append(f"{val:{alignments[i]}{widths[i]}}")
        lines.append(" ".join(cells))

    return "\n".join(lines)


def print_format_table(info: Union[MediaInfo, Dict], enable_colors: bool = True) -> None:
    """Prints a beautiful yt-dlp format table listing."""
    if isinstance(info, MediaInfo):
        formats = info.formats
        title = info.title
        media_id = info.id
    else:
        formats = [MediaFormat.from_dict(f) for f in info.get("formats", [])]
        title = info.get("title", "Unknown")
        media_id = info.get("id", "Unknown")

    print(colorize(f"[info] Available formats for {title} [{media_id}]:", TerminalColors.BOLD, enable_colors))

    headers = ["ID", "EXT", "RESOLUTION", "FPS", "CH", "|", "FILESIZE", "TBR", "PROTO", "|", "VCODEC", "ACODEC", "MORE INFO"]
    alignments = ["<", "<", "<", ">", ">", "<", ">", ">", "<", "<", "<", "<", "<"]
    rows = []

    for f in formats:
        fid = f.format_id
        ext = f.ext
        res = f.resolution
        fps = str(int(f.fps)) if f.fps else ""
        channels = "2" if f.has_audio else ""
        sep1 = "|"
        size = format_bytes(f.filesize or f.filesize_approx) if (f.filesize or f.filesize_approx) else "N/A"
        tbr = f"{int(f.get_effective_bitrate())}k" if f.get_effective_bitrate() > 0 else "N/A"
        proto = f.protocol
        sep2 = "|"
        vcodec = f.vcodec or ("none" if not f.has_video else "unknown")
        acodec = f.acodec or ("none" if not f.has_audio else "unknown")
        note = f.format_note or ""

        rows.append([fid, ext, res, fps, channels, sep1, size, tbr, proto, sep2, vcodec, acodec, note])

    table_str = format_table(headers, rows, alignments)
    print(table_str)
