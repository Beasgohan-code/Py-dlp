#!/usr/bin/env bash
# install.sh - Universal One-Line Installer Script for Linux, macOS, WSL
# Usage: curl -fsSL https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/install.sh | bash

set -e

echo "⚡ Installing Py-dlp Studio..."

# Detect Python 3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "✗ Error: Python 3 is required to install Py-dlp." >&2
    exit 1
fi

# Try pip install from git
echo "✓ Installing py-dlp..."
if $PYTHON_BIN -m pip install --upgrade git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null || \
   $PYTHON_BIN -m pip install --upgrade --break-system-packages git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null || \
   $PYTHON_BIN -m pip install --user --upgrade git+https://github.com/Beasgohan-code/Py-dlp.git 2>/dev/null; then
    echo "✓ Py-dlp installed via pip!"
else
    # Fallback to standalone binary download
    INSTALL_DIR="${HOME}/.local/bin"
    mkdir -p "$INSTALL_DIR"
    echo "✓ Downloading standalone Py-dlp binary into $INSTALL_DIR..."
    curl -fsSL -o "${INSTALL_DIR}/pydlp" "https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/dist/pydlp" || true
    chmod +x "${INSTALL_DIR}/pydlp" 2>/dev/null || true
    ln -sf "${INSTALL_DIR}/pydlp" "${INSTALL_DIR}/py-dlp" 2>/dev/null || true
fi

# Ensure ~/.local/bin is in PATH
if [ -d "${HOME}/.local/bin" ] && [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
    export PATH="${HOME}/.local/bin:${PATH}"
    echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${HOME}/.bashrc"
    [ -f "${HOME}/.zshrc" ] && echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${HOME}/.zshrc"
fi

echo "✓ Py-dlp installed successfully!"
echo "Run 'pydlp --help' or 'pydlp --doctor' to get started."
