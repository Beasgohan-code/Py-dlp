#!/usr/bin/env bash
# Py-dlp Universal One-Line Installer Script
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

# Try pip install
if command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1; then
    echo "✓ Installing py-dlp via pip..."
    $PYTHON_BIN -m pip install --upgrade py-dlp 2>/dev/null || $PYTHON_BIN -m pip install --upgrade py-dlp --break-system-packages 2>/dev/null || $PYTHON_BIN -m pip install --user --upgrade py-dlp || {
        INSTALL_DIR="${HOME}/.local/bin"
        mkdir -p "$INSTALL_DIR"
        echo "✓ Downloading standalone Py-dlp binary into $INSTALL_DIR..."
        curl -fsSL -o "${INSTALL_DIR}/pydlp" "https://github.com/Beasgohan-code/Py-dlp/releases/latest/download/pydlp" || true
        chmod +x "${INSTALL_DIR}/pydlp" 2>/dev/null || true
        ln -sf "${INSTALL_DIR}/pydlp" "${INSTALL_DIR}/py-dlp" 2>/dev/null || true
    }
else
    # Fallback to standalone binary download
    INSTALL_DIR="${HOME}/.local/bin"
    mkdir -p "$INSTALL_DIR"
    echo "✓ Downloading standalone Py-dlp binary into $INSTALL_DIR..."
    curl -fsSL -o "${INSTALL_DIR}/pydlp" "https://github.com/Beasgohan-code/Py-dlp/releases/latest/download/pydlp"
    chmod +x "${INSTALL_DIR}/pydlp"
    ln -sf "${INSTALL_DIR}/pydlp" "${INSTALL_DIR}/py-dlp"
fi

echo "✓ Py-dlp installed successfully!"
echo "Run 'pydlp --help' or 'pydlp --doctor' to get started."
