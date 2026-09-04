#!/usr/bin/env python3
"""Builds wheel, sdist, and standalone zipapp release packages."""

import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    os.chdir(ROOT_DIR)
    print("[build] Building distribution packages...")

    # Build standalone bundle
    subprocess.run([sys.executable, "bundle.py"], check=True)

    # Build wheel and sdist
    subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], check=True)

    print("[build] Completed all builds in dist/:")
    for f in os.listdir(os.path.join(ROOT_DIR, "dist")):
        print(f"  - dist/{f}")


if __name__ == "__main__":
    main()
