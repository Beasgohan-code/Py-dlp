#!/usr/bin/env bash
# package.sh - Packages compiled static FFmpeg binaries into release archives with SHA256 sums

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/util/vars.sh"

setup_target_env

PKG_NAME_BASE="ffmpeg-${FFMPEG_BRANCH}-latest-${TARGET}-gpl"
PKG_DIR="${BUILD_DIR}/${PKG_NAME_BASE}"
mkdir -p "${PKG_DIR}/bin" "${ARTIFACTS_DIR}"

log_info "Preparing package directory: ${PKG_DIR}..."

# Copy Binaries
cp -f "${INSTALL_DIR}/bin/ffmpeg${EXE_EXT}" "${PKG_DIR}/bin/"
cp -f "${INSTALL_DIR}/bin/ffprobe${EXE_EXT}" "${PKG_DIR}/bin/"

# Copy License & Readme
cat << EOF > "${PKG_DIR}/README.txt"
FFmpeg Static Build for yt-dlp
==============================
Target: ${TARGET}
Branch: ${FFMPEG_BRANCH}
Generated on: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

This build is customized and optimized specifically for yt-dlp integration.
It contains static builds of:
  - bin/ffmpeg${EXE_EXT}
  - bin/ffprobe${EXE_EXT}

Features & Patches:
  - Enabled HTTPS, HLS, DASH protocols via OpenSSL & libxml2
  - Video codecs: x264, x265, libvpx (VP8/VP9), libdav1d (AV1)
  - Audio codecs: libmp3lame, libopus, libvorbis
  - Subtitles: libass, libfreetype, libfribidi
  - yt-dlp patches: Non-standard HEVC in FLV decoding, AAC HLS truncation fix

Usage with yt-dlp:
  yt-dlp --ffmpeg-location ./bin/ "https://www.youtube.com/watch?v=..."
EOF

cp -f "${SRC_DIR}/ffmpeg/LICENSE.md" "${PKG_DIR}/LICENSE.txt" 2>/dev/null || \
cp -f "${SRC_DIR}/ffmpeg/COPYING.GPLv3" "${PKG_DIR}/LICENSE.txt" 2>/dev/null || \
cat << EOF > "${PKG_DIR}/LICENSE.txt"
GNU GENERAL PUBLIC LICENSE Version 3
https://www.gnu.org/licenses/gpl-3.0.html
EOF

# Create Release Archive
cd "${BUILD_DIR}"
ARCHIVE_NAME="${PKG_NAME_BASE}${ARCHIVE_EXT}"
ARCHIVE_PATH="${ARTIFACTS_DIR}/${ARCHIVE_NAME}"

log_info "Creating archive: ${ARCHIVE_PATH}..."

if [ "${ARCHIVE_EXT}" = ".zip" ]; then
    zip -r -9 "${ARCHIVE_PATH}" "${PKG_NAME_BASE}"
else
    tar -cJf "${ARCHIVE_PATH}" "${PKG_NAME_BASE}"
fi

# Generate SHA256 Checksum
cd "${ARTIFACTS_DIR}"
sha256sum "${ARCHIVE_NAME}" > "${ARCHIVE_NAME}.sha256"

log_success "Package created successfully: ${ARCHIVE_PATH}"
log_success "Checksum: $(cat "${ARCHIVE_NAME}.sha256")"
