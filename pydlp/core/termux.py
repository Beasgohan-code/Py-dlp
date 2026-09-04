"""Termux (Android) environment integration and automated configuration for Py-dlp."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from pydlp.core.progress import TerminalColors, colorize


def is_termux() -> bool:
    """Checks if currently running in a Termux environment on Android."""
    return bool(
        os.environ.get("TERMUX_VERSION")
        or os.environ.get("TERMUX_APK_RELEASE")
        or os.path.exists("/data/data/com.termux")
        or (os.environ.get("PREFIX", "").startswith("/data/data/com.termux"))
    )


def get_termux_download_dir() -> Path:
    """Returns the preferred download directory path for Termux users."""
    shared_downloads = Path.home() / "storage" / "shared" / "Download"
    if shared_downloads.exists():
        return shared_downloads

    sdcard_downloads = Path("/sdcard/Download")
    if sdcard_downloads.exists():
        return sdcard_downloads

    home_downloads = Path.home() / "downloads"
    home_downloads.mkdir(parents=True, exist_ok=True)
    return home_downloads


def send_termux_notification(title: str, content: str, priority: str = "high") -> bool:
    """Sends a native Android notification via termux-api if installed."""
    if not is_termux():
        return False

    termux_notify = shutil.which("termux-notification")
    if not termux_notify:
        return False

    try:
        subprocess.run(
            [
                termux_notify,
                "-t",
                f"Py-dlp: {title}",
                "-c",
                content,
                "--priority",
                priority,
                "--id",
                "pydlp_download",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return True
    except Exception:
        return False


def setup_termux_environment() -> int:
    """Configures Termux storage permissions, default config, and share sheet url-opener."""
    color = True
    print(colorize("📱 Setting up Py-dlp for Termux (Android)...", TerminalColors.BOLD, color))
    print("=" * 60)

    # 1. Check storage permissions
    storage_dir = Path.home() / "storage"
    if not storage_dir.exists():
        print("  ! Requesting Android storage permission via 'termux-setup-storage'...")
        try:
            subprocess.run(["termux-setup-storage"], check=False)
            print("  ✓ Storage setup initiated. Please accept the Android storage permission popup.")
        except Exception:
            print("  ! Please run 'termux-setup-storage' to grant download permissions to internal storage.")
    else:
        print("  ✓ Storage access: Granted (~/storage/shared/Download)")

    # 2. Setup termux-url-opener for Android Share Sheet integration
    bin_dir = Path.home() / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    opener_path = bin_dir / "termux-url-opener"

    opener_script = """#!/data/data/com.termux/files/usr/bin/bash
# Py-dlp Termux Share Sheet Handler
# Automatically downloads URLs shared from YouTube, TikTok, Instagram, Twitter, etc.

url="$1"
if [ -z "$url" ]; then
    echo "No URL provided."
    exit 1
fi

echo "⚡ Py-dlp downloading shared media: $url"

# Run Py-dlp with standard download directory
if command -v pydlp >/dev/null 2>&1; then
    pydlp "$url"
elif command -v py-dlp >/dev/null 2>&1; then
    py-dlp "$url"
else
    python3 -m pydlp "$url"
fi

if command -v termux-notification >/dev/null 2>&1; then
    termux-notification -t "Py-dlp" -c "Download finished!" --priority high
fi
"""
    opener_path.write_text(opener_script, encoding="utf-8")
    opener_path.chmod(0o755)
    print(f"  ✓ Android Share Sheet integration: Installed ({opener_path})")
    print("    -> Now you can tap 'Share' on any video in YouTube, TikTok, etc. and choose 'Termux' to download instantly!")

    # 3. Create default configuration file in ~/.config/pydlp/config
    config_dir = Path.home() / ".config" / "pydlp"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config"

    default_download_path = str(get_termux_download_dir())
    config_content = f"""# Py-dlp Termux Default Configuration
-P "{default_download_path}"
-o "%(title)s.%(ext)s"
--concurrent-fragments 5
--no-warnings
"""
    if not config_file.exists():
        config_file.write_text(config_content, encoding="utf-8")
        print(f"  ✓ Config file created: {config_file} (Default: {default_download_path})")
    else:
        print(f"  ✓ Existing config file preserved: {config_file}")

    # 4. Check FFmpeg in Termux
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        print(f"  ✓ FFmpeg detected: {ffmpeg_bin}")
    else:
        print("  ! FFmpeg not found. Install it with: pkg install ffmpeg -y")

    print("=" * 60)
    print(colorize("✓ Termux setup completed successfully! Ready for downloads.", TerminalColors.GREEN, color))
    return 0
