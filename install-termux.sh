#!/data/data/com.termux/files/usr/bin/bash
# install-termux.sh - One-line automated installer and setup for Py-dlp on Android (Termux)
# Usage: curl -fsSL https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/install-termux.sh | bash

set -e

echo "📱 Installing Py-dlp Studio for Termux (Android)..."

# 1. Update pkg & install Python, FFmpeg, git, curl
echo "✓ Updating and upgrading package repositories..."
pkg update -y && pkg upgrade -y || apt-get update -y && apt-get upgrade -y

echo "✓ Installing Python 3, FFmpeg, and required tools..."
pkg install -y python ffmpeg libx265 curl git termux-api || apt-get install -y python ffmpeg curl git

# 2. Install Py-dlp from GitHub repository
echo "✓ Installing Py-dlp..."
if pip install --upgrade git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null || \
   pip install --upgrade --break-system-packages git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null || \
   pip install --user --upgrade git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null; then
    echo "✓ Py-dlp installed via pip!"
else
    echo "✓ Installing Py-dlp standalone engine..."
    INSTALL_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
    mkdir -p "$INSTALL_DIR" "${HOME}/.pydlp"
    rm -rf "${HOME}/.pydlp"
    git clone --depth 1 https://github.com/Beasgohan-code/Py-dlp.git "${HOME}/.pydlp"
    
    cat << 'EOF' > "${INSTALL_DIR}/pydlp"
#!/data/data/com.termux/files/usr/bin/python3
import sys, os
sys.path.insert(0, os.path.expanduser("~/.pydlp"))
from pydlp.main import main
if __name__ == "__main__":
    sys.exit(main())
EOF
    chmod +x "${INSTALL_DIR}/pydlp"
    ln -sf "${INSTALL_DIR}/pydlp" "${INSTALL_DIR}/py-dlp"
fi

# Ensure binary is in path
if [ -d "${HOME}/.local/bin" ] && [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
    export PATH="${HOME}/.local/bin:${PATH}"
    echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc
fi

# 3. Setup Termux storage and URL opener
echo "✓ Configuring storage and Android Share Sheet integration..."
if command -v pydlp >/dev/null 2>&1; then
    pydlp --setup-termux
elif command -v py-dlp >/dev/null 2>&1; then
    py-dlp --setup-termux
elif [ -f "${PREFIX:-/data/data/com.termux/files/usr}/bin/pydlp" ]; then
    "${PREFIX:-/data/data/com.termux/files/usr}/bin/pydlp" --setup-termux
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
