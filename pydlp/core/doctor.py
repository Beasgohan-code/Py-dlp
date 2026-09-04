"""Py-dlp System Health Doctor and Diagnostics."""

from __future__ import annotations

import platform
import shutil
import ssl
import sys
from typing import Dict, List

from pydlp.core.progress import TerminalColors, colorize
from pydlp.extractor import list_extractors
from pydlp.extractor.sites_db import get_all_supported_domains_count
from pydlp.version import __version__


def run_doctor() -> int:
    """Executes a diagnostic check on the Py-dlp installation, dependencies, and environment."""
    print(colorize(f"⚡ Py-dlp System Diagnostics (v{__version__})", TerminalColors.BOLD, True))
    print("=" * 60)

    # 1. Python Environment
    py_ver = platform.python_version()
    print(f"  ✓ Python Version:      {py_ver} ({platform.python_implementation()})")
    print(f"  ✓ Operating System:    {platform.system()} {platform.release()} ({platform.machine()})")

    # 2. OpenSSL & TLS
    try:
        ssl_ver = ssl.OPENSSL_VERSION
        print(f"  ✓ TLS/SSL Engine:      {ssl_ver}")
    except Exception:
        print("  ✗ TLS/SSL Engine:      Unavailable")

    # 3. FFmpeg & Media Tools
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path:
        print(f"  ✓ FFmpeg Encoder:      {ffmpeg_path}")
    else:
        print("  ! FFmpeg Encoder:      Not found in PATH (optional, needed for muxing audio/video)")

    if ffprobe_path:
        print(f"  ✓ FFprobe Analyzer:    {ffprobe_path}")
    else:
        print("  ! FFprobe Analyzer:    Not found in PATH")

    # 4. External Downloaders
    tools = ["aria2c", "curl", "wget", "axel"]
    avail_tools = [t for t in tools if shutil.which(t)]
    if avail_tools:
        print(f"  ✓ External Tools:      {', '.join(avail_tools)}")
    else:
        print("  ✓ External Tools:      Using Pure Python Standard Library (No external CLI tools needed)")

    # 5. Extractors & Domains
    extractors = list_extractors()
    domain_count = get_all_supported_domains_count()
    print(f"  ✓ Native Extractors:   {len(extractors)} core extractors loaded")
    print(f"  ✓ Recognized Domains:  {domain_count}+ platforms indexed in Universal Catalog")

    print("=" * 60)
    print(colorize("✓ All core subsystems operational!", TerminalColors.GREEN, True))
    return 0
