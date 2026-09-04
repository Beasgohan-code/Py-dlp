"""Interactive stream picker and TUI format explorer for Py-dlp."""

from __future__ import annotations

import sys
from typing import List, Optional

from pydlp.core.progress import TerminalColors, colorize, format_table
from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.utils import format_bytes


class InteractiveSelector:
    """Interactively display media formats and prompt user for format selection."""

    def __init__(self, color: bool = True):
        self.color = color

    def display_and_select(self, info: MediaInfo) -> List[MediaFormat]:
        """Display formats in a tabular view and prompt user for selection."""
        if not info.formats:
            print(colorize("No formats available for interactive selection.", TerminalColors.YELLOW, self.color))
            return []

        print()
        print(colorize("╔══════════════════════════════════════════════════════════════════════════════╗", TerminalColors.CYAN, self.color))
        print(colorize(f"║ INTERACTIVE FORMAT SELECTOR: {info.title[:55]:<55} ║", TerminalColors.BOLD, self.color))
        print(colorize("╚══════════════════════════════════════════════════════════════════════════════╝", TerminalColors.CYAN, self.color))

        headers = ["#", "ID", "EXT", "RESOLUTION", "FPS", "BITRATE", "FILESIZE", "CODECS", "NOTE"]
        rows = []

        for idx, fmt in enumerate(info.formats, 1):
            res = fmt.resolution or (f"{fmt.width}x{fmt.height}" if fmt.width and fmt.height else (f"{fmt.height}p" if fmt.height else "audio only"))
            fps = f"{int(fmt.fps)}" if fmt.fps else "--"
            br = f"{int(fmt.tbr)}k" if fmt.tbr else (f"{int(fmt.vbr)}k" if fmt.vbr else "--")
            size = format_bytes(fmt.filesize) if fmt.filesize else "--"
            codecs = []
            if fmt.vcodec and fmt.vcodec != "none":
                codecs.append(fmt.vcodec[:10])
            if fmt.acodec and fmt.acodec != "none":
                codecs.append(fmt.acodec[:10])
            codec_str = "+".join(codecs) if codecs else "--"
            note = fmt.format_note or fmt.format or ""

            # Truncate note if long
            if len(note) > 15:
                note = note[:12] + "..."

            rows.append([
                str(idx),
                fmt.format_id or "--",
                fmt.ext or "--",
                res,
                fps,
                br,
                size,
                codec_str,
                note,
            ])

        print(format_table(headers, rows))
        print()
        print(colorize("Selection Options:", TerminalColors.BOLD, self.color))
        print("  - Single format ID or number: '1', '137', 'best', 'worst'")
        print("  - Video + Audio combo: '137+140', 'bestvideo+bestaudio'")
        print("  - Resolution target: '1080', '720', '480', 'audio'")
        print("  - Press Enter to use default best quality.")
        print()

        try:
            prompt_text = colorize("Select format code(s) > ", TerminalColors.GREEN, self.color)
            user_choice = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nInteractive selection cancelled.")
            sys.exit(0)

        if not user_choice or user_choice.lower() in ("best", "b", "default"):
            return []  # PyDLP will fallback to standard default format selector

        # Match user choice against formats
        return self._resolve_choice(user_choice, info.formats)

    def _resolve_choice(self, choice: str, formats: List[MediaFormat]) -> List[MediaFormat]:
        """Resolve user choice string into a list of MediaFormats."""
        choice = choice.strip()

        # Check if index number (e.g. '1', '2')
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(formats):
                return [formats[idx - 1]]

        # Check for '+' combination (e.g. '137+140' or '2+4')
        if "+" in choice:
            parts = [p.strip() for p in choice.split("+")]
            selected = []
            for part in parts:
                match = self._find_single_format(part, formats)
                if match and match not in selected:
                    selected.append(match)
            if selected:
                return selected

        single_match = self._find_single_format(choice, formats)
        if single_match:
            return [single_match]

        print(colorize(f"Warning: Could not match '{choice}'. Using best available format.", TerminalColors.YELLOW, self.color))
        return []

    def _find_single_format(self, query: str, formats: List[MediaFormat]) -> Optional[MediaFormat]:
        query_lower = query.lower()

        # Check index
        if query.isdigit():
            idx = int(query)
            if 1 <= idx <= len(formats):
                return formats[idx - 1]

        # Check format_id exact
        for f in formats:
            if f.format_id and f.format_id.lower() == query_lower:
                return f

        # Check resolution keywords
        if query_lower in ("audio", "audio-only", "ba", "bestaudio"):
            audios = [f for f in formats if f.acodec != "none" and (not f.vcodec or f.vcodec == "none")]
            if audios:
                return sorted(audios, key=lambda x: (x.tbr or x.abr or 0), reverse=True)[0]

        # Check height (e.g. '1080', '1080p', '720', '720p')
        height_str = query_lower.rstrip("p")
        if height_str.isdigit():
            target_h = int(height_str)
            matching_h = [f for f in formats if f.height == target_h]
            if matching_h:
                return sorted(matching_h, key=lambda x: (x.tbr or x.vbr or 0), reverse=True)[0]

        # Check format note or ext
        for f in formats:
            if f.ext and f.ext.lower() == query_lower:
                return f
            if f.format_note and query_lower in f.format_note.lower():
                return f

        return None
