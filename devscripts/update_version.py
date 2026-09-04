#!/usr/bin/env python3
"""Updates Py-dlp version string to today's date."""

import datetime
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT_DIR, "pydlp", "version.py")
PYPROJECT_FILE = os.path.join(ROOT_DIR, "pyproject.toml")
SETUP_FILE = os.path.join(ROOT_DIR, "setup.py")


def main():
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y.%m.%d")
    print(f"[version] Bumping version to {today}...")

    # Update version.py
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{today}"', content)
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Update pyproject.toml
    with open(PYPROJECT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{today}"', content)
    with open(PYPROJECT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Update setup.py
    with open(SETUP_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r'version\s*=\s*"[^"]+"', f'version="{today}"', content)
    with open(SETUP_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[version] Successfully updated version to {today} across all files.")


if __name__ == "__main__":
    main()
