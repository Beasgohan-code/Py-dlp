"""Self-updater engine for Py-dlp.

Supports updating standalone binary distributions and pip packages via GitHub Releases and PyPI.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import tempfile
import urllib.request
from typing import Optional, Tuple

from pydlp.core.progress import TerminalColors, colorize
from pydlp.version import __version__

logger = logging.getLogger("pydlp.updater")


class SelfUpdater:
    """Handles checking for updates, downloading new release binaries, and updating pip packages."""

    GITHUB_REPO = "Beasgohan-code/Py-dlp"

    def __init__(self, color: bool = True):
        self.color = color

    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """Check if a newer version is available on GitHub."""
        url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Py-dlp-Updater"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latest_tag = data.get("tag_name", "").lstrip("v")
                if latest_tag and latest_tag != __version__:
                    return True, latest_tag
                return False, __version__
        except Exception as e:
            logger.debug(f"Update check failed: {e}")
            return False, None

    def update(self) -> int:
        """Executes the self-update process."""
        print(colorize("⚡ Checking for Py-dlp updates...", TerminalColors.CYAN, self.color))
        has_update, latest_ver = self.check_for_updates()

        if not has_update:
            print(colorize(f"✓ Py-dlp is up to date (v{__version__})", TerminalColors.GREEN, self.color))
            return 0

        print(colorize(f"A new version is available: v{latest_ver} (Current: v{__version__})", TerminalColors.YELLOW, self.color))

        # Check if running as a standalone script/binary or installed via pip
        exe_path = os.path.realpath(sys.argv[0])

        if getattr(sys, "frozen", False) or exe_path.endswith(("/pydlp", "/py-dlp", ".zipapp")):
            return self._update_binary(latest_ver, exe_path)
        else:
            return self._update_pip(latest_ver)

    def _update_binary(self, version: str, target_path: str) -> int:
        """Download new binary and atomically replace current executable."""
        download_url = f"https://github.com/{self.GITHUB_REPO}/releases/download/v{version}/pydlp"
        print(colorize(f"Downloading release binary from {download_url}...", TerminalColors.BOLD, self.color))

        try:
            temp_fd, temp_path = tempfile.mkstemp(prefix="pydlp-update-")
            os.close(temp_fd)

            req = urllib.request.Request(download_url, headers={"User-Agent": "Py-dlp-Updater"})
            with urllib.request.urlopen(req, timeout=30.0) as resp, open(temp_path, "wb") as f:
                f.write(resp.read())

            os.chmod(temp_path, 0o755)
            # Atomic replacement
            shutil.move(temp_path, target_path)
            print(colorize(f"✓ Successfully updated Py-dlp to v{version}!", TerminalColors.GREEN, self.color))
            return 0
        except Exception as e:
            print(colorize(f"✗ Failed to update binary: {e}", TerminalColors.RED, self.color), file=sys.stderr)
            return 1

    def _update_pip(self, version: str) -> int:
        """Run pip install --upgrade py-dlp."""
        import subprocess

        print(colorize("Updating via pip...", TerminalColors.BOLD, self.color))
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "py-dlp"]
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            print(colorize(f"✓ Successfully upgraded py-dlp via pip!", TerminalColors.GREEN, self.color))
        return res.returncode
