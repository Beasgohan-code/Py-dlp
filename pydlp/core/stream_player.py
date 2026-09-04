"""Direct media streaming into video players (mpv, vlc, ffplay) without saving to disk."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import PyDLPError
from pydlp.core.types import MediaFormat, MediaInfo


class StreamPlayer:
    """Streams resolved media format URLs directly into external media players."""

    SUPPORTED_PLAYERS = ["mpv", "vlc", "ffplay", "iina", "mplayer"]

    def __init__(self, player_cmd: Optional[str] = None):
        self.player_cmd = player_cmd or self._detect_default_player()

    def _detect_default_player(self) -> str:
        for p in self.SUPPORTED_PLAYERS:
            if shutil.which(p):
                return p
        return "mpv"

    def play(self, info: MediaInfo, fmt: MediaFormat) -> int:
        """Launches player with the stream URL."""
        if not fmt.url:
            raise PyDLPError(f"Format {fmt.format_id} has no valid streaming URL")

        player = self.player_cmd
        if not shutil.which(player):
            raise PyDLPError(f"Player executable '{player}' not found in PATH")

        print(f"[play] Playing '{info.title}' via {player}...")
        cmd = [player, fmt.url]
        if player == "mpv":
            cmd.extend([f"--title={info.title}"])
            if fmt.http_headers:
                for k, v in fmt.http_headers.items():
                    cmd.append(f"--http-header-fields={k}: {v}")

        proc = subprocess.run(cmd)
        return proc.returncode
