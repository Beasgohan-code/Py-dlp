"""ANSI 24-bit TrueColor ASCII/Half-Block terminal media visualizer for Py-dlp.

Renders video thumbnails and frames directly into the terminal window.
"""

from __future__ import annotations

import io
import math
import shutil
import struct
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


class TerminalMediaPreview:
    """Renders images/thumbnails directly into terminal text using ANSI 24-bit color half-blocks."""

    ASCII_CHARS = " .:-=+*#%@"

    @staticmethod
    def render_ansi_halfblock(
        rgb_pixels: List[List[Tuple[int, int, int]]], width: int, height: int
    ) -> str:
        """Renders RGB matrix using unicode half-block characters (▀) for double vertical resolution."""
        lines = []
        for y in range(0, height - 1, 2):
            line_chunks = []
            for x in range(width):
                top_r, top_g, top_b = rgb_pixels[y][x]
                bot_r, bot_g, bot_b = rgb_pixels[y + 1][x]
                # Top pixel is foreground, bottom is background
                line_chunks.append(
                    f"\033[38;2;{top_r};{top_g};{top_b}m\033[48;2;{bot_r};{bot_g};{bot_b}m▀\033[0m"
                )
            lines.append("".join(line_chunks))
        return "\n".join(lines)

    @classmethod
    def generate_synthetic_preview(
        cls, title: str, category: str = "MEDIA", width: int = 50, height: int = 20
    ) -> str:
        """Generates a stylish ANSI gradient canvas with title metadata overlay."""
        # Ensure even height for half-block rendering
        height = height if height % 2 == 0 else height + 1
        rgb_matrix = []

        # Color gradient based on category hash
        base_h = abs(hash(category)) % 360
        for y in range(height):
            row = []
            for x in range(width):
                # Diagonal plasma / gradient effect
                r = int(127 + 127 * math.sin(x / 8.0 + base_h))
                g = int(127 + 127 * math.sin(y / 6.0 + base_h / 2.0))
                b = int(127 + 127 * math.cos((x + y) / 10.0))
                row.append((max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
            rgb_matrix.append(row)

        rendered = cls.render_ansi_halfblock(rgb_matrix, width, height)
        header = f"\033[1;36m▶ PREVIEW:\033[0m \033[1;37m{title[:width]}\033[0m"
        return f"{header}\n{rendered}"

    @classmethod
    def render_thumbnail_url_or_file(
        cls, thumbnail_source: str, title: str = "", max_width: int = 60
    ) -> str:
        """Fetches/reads a thumbnail or generates a vibrant preview card."""
        term_size = shutil.get_terminal_size((80, 24))
        target_w = min(max_width, term_size.columns - 4)
        target_h = int(target_w * 0.45)
        target_h = target_h if target_h % 2 == 0 else target_h + 1

        # Check if FFmpeg is available to extract raw PPM stream
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin and (thumbnail_source.startswith("http") or Path(thumbnail_source).exists()):
            try:
                cmd = [
                    ffmpeg_bin,
                    "-loglevel",
                    "quiet",
                    "-i",
                    thumbnail_source,
                    "-vf",
                    f"scale={target_w}:{target_h}:flags=lanczos",
                    "-vframes",
                    "1",
                    "-f",
                    "image2pipe",
                    "-vcodec",
                    "ppm",
                    "-",
                ]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
                if proc.returncode == 0 and proc.stdout.startswith(b"P6"):
                    return cls._parse_ppm_and_render(proc.stdout, title)
            except Exception:
                pass

        return cls.generate_synthetic_preview(title or thumbnail_source, "PYDLP", target_w, target_h)

    @classmethod
    def _parse_ppm_and_render(cls, ppm_bytes: bytes, title: str) -> str:
        """Parses raw binary PPM image data into RGB pixel grid and renders half-blocks."""
        lines = ppm_bytes.split(b"\n", 3)
        if len(lines) < 4 or lines[0] != b"P6":
            return ""

        dims = lines[1].split()
        if len(dims) < 2:
            dims = lines[2].split()
            pixel_data = lines[3]
        else:
            pixel_data = lines[3]

        width = int(dims[0])
        height = int(dims[1])
        height = height if height % 2 == 0 else height - 1

        rgb_matrix = []
        idx = 0
        for y in range(height):
            row = []
            for x in range(width):
                if idx + 3 <= len(pixel_data):
                    r, g, b = pixel_data[idx : idx + 3]
                    row.append((r, g, b))
                    idx += 3
                else:
                    row.append((0, 0, 0))
            rgb_matrix.append(row)

        header = f"\033[1;36m▶ PREVIEW:\033[0m \033[1;37m{title[:width]}\033[0m"
        return f"{header}\n{cls.render_ansi_halfblock(rgb_matrix, width, height)}"
