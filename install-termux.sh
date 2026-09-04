#!/data/data/com.termux/files/usr/bin/bash
# install-termux.sh - One-line automated installer and setup for Py-dlp on Android (Termux)
# Usage: curl -fsSL https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/install-termux.sh | bash

set -e

echo "📱 Installing Py-dlp for Termux (Android)..."

# 1. Update pkg & install Python, FFmpeg, git, curl
echo "✓ Updating package repositories..."
pkg update -y || apt-get update -y

echo "✓ Installing Python 3, FFmpeg, and required tools..."
pkg install -y python ffmpeg curl git termux-api || apt-get install -y python ffmpeg curl git

# 2. Install Py-dlp via pip
echo "✓ Installing Py-dlp via pip..."
pip install --upgrade py-dlp || pip install --upgrade py-dlp --break-system-packages || pip install --user --upgrade py-dlp

# 3. Setup Termux storage and URL opener
echo "✓ Configuring storage and Android Share Sheet integration..."
if command -v pydlp >/dev/null 2>&1; then
    pydlp --setup-termux
elif command -v py-dlp >/dev/null 2>&1; then
    py-dlp --setup-termux
else
    python3 -m pydlp --setup-termux
fi

echo ""
echo "============================================================"
echo "🎉 Py-dlp is successfully installed on Termux!"
echo "============================================================"
echo "Usage Examples:"
echo "  1. CLI Download:  pydlp 'https://youtu.be/dQw4w9WgXcQ'"
echo "  2. MP3 Audio:     pydlp -x --audio-format mp3 'https://youtu.be/...'"
echo "  3. Share Sheet:   Tap 'Share' in YouTube/TikTok and choose 'Termux'!"
echo "  4. Diagnostics:   pydlp --doctor"
echo "============================================================"
