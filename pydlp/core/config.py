"""Hierarchical configuration file parser for Py-dlp.

Reads options from system, user, and portable configuration files.
"""

from __future__ import annotations

import os
import shlex
import sys
from typing import List, Optional


class ConfigFileParser:
    """Discovers and parses configuration files into command line argument lists."""

    @classmethod
    def get_default_config_locations(cls) -> List[str]:
        """Returns list of default configuration file paths in priority order."""
        paths: List[str] = []

        # 1. Portable config in current working directory
        paths.append(os.path.abspath("pydlp.conf"))

        # 2. User home config
        home = os.path.expanduser("~")
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            if appdata:
                paths.append(os.path.join(appdata, "pydlp", "config.txt"))
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
            paths.append(os.path.join(xdg_config, "pydlp", "config"))
            paths.append(os.path.join(home, ".pydlprc"))

        # 3. System-wide config
        if sys.platform != "win32":
            paths.append("/etc/pydlp.conf")

        return paths

    @classmethod
    def load_config_args(cls, custom_path: Optional[str] = None, ignore_config: bool = False) -> List[str]:
        """Loads and parses command-line flags from config files."""
        if ignore_config:
            return []

        if custom_path:
            candidates = [custom_path]
        else:
            candidates = cls.get_default_config_locations()

        args: List[str] = []
        for path in candidates:
            if os.path.isfile(path):
                args.extend(cls._parse_file(path))
                # Only load first valid config file found
                break

        return args

    @staticmethod
    def _parse_file(filepath: str) -> List[str]:
        """Parse flags from config file line by line."""
        tokens: List[str] = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith(";"):
                        continue
                    # Split line into arguments respecting quotes
                    tokens.extend(shlex.split(line))
        except Exception:
            pass
        return tokens
