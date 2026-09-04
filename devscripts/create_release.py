#!/usr/bin/env python3
"""Automated release artifact builder and GitHub release manager for Py-dlp."""

from __future__ import annotations

import os
import subprocess
import sys

from pydlp.version import __version__


def create_release():
    print(f"[release] Creating Py-dlp Release v{__version__}...")

    # 1. Run tests
    print("[release] Running full test suite...")
    test_proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
    if test_proc.returncode != 0:
        print("[release] Error: Tests failed. Aborting release.")
        sys.exit(1)

    # 2. Build distribution packages & standalone executable
    print("[release] Building distributions and standalone binary...")
    build_proc = subprocess.run([sys.executable, "devscripts/build_dist.py"])
    if build_proc.returncode != 0:
        print("[release] Error: Distribution build failed.")
        sys.exit(1)

    # 3. List generated release assets
    dist_dir = os.path.abspath("dist")
    print("\n[release] Generated Release Assets:")
    if os.path.exists(dist_dir):
        for f in sorted(os.listdir(dist_dir)):
            path = os.path.join(dist_dir, f)
            size_kb = os.path.getsize(path) / 1024.0
            print(f"  ✓ {f:<35} ({size_kb:.1f} KB)")

    print(f"\n[release] Py-dlp v{__version__} release packages are ready in dist/!")


if __name__ == "__main__":
    create_release()
