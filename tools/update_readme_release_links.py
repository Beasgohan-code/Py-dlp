#!/usr/bin/env python3
"""
tools/update_readme_release_links.py - Generates/Updates the Download Matrix Table in README.md
"""

import re
import sys
from pathlib import Path

REPO_OWNER = "Beasgohan-code"
REPO_NAME = "Py-dlp"

DOWNLOAD_MATRIX_TEMPLATE = """
<!-- BEGIN_DOWNLOAD_MATRIX -->
| Platform / Architecture | Variant | FFmpeg Master (Nightly) | Latest Stable Release | Checksums |
| :--- | :--- | :--- | :--- | :--- |
| **Windows 64-bit (x64)** | GPL Static | [⬇️ `.zip`]({base_url}/ffmpeg-master-latest-win64-gpl.zip) | [⬇️ `.zip`]({base_url}/ffmpeg-release-latest-win64-gpl.zip) | [SHA256]({base_url}/ffmpeg-master-latest-win64-gpl.zip.sha256) |
| **Windows 32-bit (x86)** | GPL Static | [⬇️ `.zip`]({base_url}/ffmpeg-master-latest-win32-gpl.zip) | [⬇️ `.zip`]({base_url}/ffmpeg-release-latest-win32-gpl.zip) | [SHA256]({base_url}/ffmpeg-master-latest-win32-gpl.zip.sha256) |
| **Linux 64-bit (x86_64)** | GPL Static | [⬇️ `.tar.xz`]({base_url}/ffmpeg-master-latest-linux64-gpl.tar.xz) | [⬇️ `.tar.xz`]({base_url}/ffmpeg-release-latest-linux64-gpl.tar.xz) | [SHA256]({base_url}/ffmpeg-master-latest-linux64-gpl.tar.xz.sha256) |
| **Linux ARM64 (aarch64)** | GPL Static | [⬇️ `.tar.xz`]({base_url}/ffmpeg-master-latest-linuxarm64-gpl.tar.xz) | [⬇️ `.tar.xz`]({base_url}/ffmpeg-release-latest-linuxarm64-gpl.tar.xz) | [SHA256]({base_url}/ffmpeg-master-latest-linuxarm64-gpl.tar.xz.sha256) |
<!-- END_DOWNLOAD_MATRIX -->
"""


def update_readme(readme_path: Path, tag: str = "latest"):
    if not readme_path.exists():
        print(f"Error: {readme_path} not found", file=sys.stderr)
        return

    content = readme_path.read_text(encoding="utf-8")
    base_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{tag}"
    new_matrix = DOWNLOAD_MATRIX_TEMPLATE.format(base_url=base_url).strip()

    pattern = r"<!-- BEGIN_DOWNLOAD_MATRIX -->[\s\S]*?<!-- END_DOWNLOAD_MATRIX -->"
    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_matrix, content)
    else:
        # Append if not found
        updated_content = content + "\n\n## ⬇️ Downloads\n\n" + new_matrix

    readme_path.write_text(updated_content, encoding="utf-8")
    print(f"Successfully updated download matrix in {readme_path}")


if __name__ == "__main__":
    readme = Path(__file__).resolve().parent.parent / "README.md"
    tag_arg = sys.argv[1] if len(sys.argv) > 1 else "latest"
    update_readme(readme, tag_arg)
