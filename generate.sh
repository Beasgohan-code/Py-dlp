#!/usr/bin/env bash
# generate.sh - Inspects library recipes and generates build plan / dynamic Dockerfile

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/util/vars.sh"

TARGET="${1:-${TARGET}}"
FFMPEG_BRANCH="${2:-${FFMPEG_BRANCH}}"

cat << EOF
# ==============================================================================
# Dynamic FFmpeg Static Build Plan for yt-dlp
# Target:        ${TARGET}
# FFmpeg Branch: ${FFMPEG_BRANCH}
# Generated:     $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# ==============================================================================

Build Stages:
  1. Environment Preparation (Target: ${TARGET})
  2. Download Sources & Checksums (download.sh)
  3. Compile Static Prerequisite Libraries:
EOF

for script in "${SCRIPT_DIR}"/scripts.d/[0-5]*.sh; do
    if [ -f "${script}" ]; then
        echo "     - $(basename "${script}")"
    fi
done

cat << EOF
  4. Patch FFmpeg with yt-dlp Compatibility Fixes:
     - 0001-flv-hevc-decoding.patch (HEVC in FLV demuxing)
     - 0002-hls-aac-truncation.patch (HLS AAC stream truncation fix)
     - 0003-win32-vulkan-null.patch (Win32 Vulkan handle fix)
  5. Compile Static FFmpeg & FFprobe (60-ffmpeg.sh)
  6. Strip Binaries & Package Archive with SHA256 Sums (package.sh)

Expected Output Artifacts:
  - artifacts/ffmpeg-${FFMPEG_BRANCH}-latest-${TARGET}-gpl$( [ "${TARGET:0:3}" = "win" ] && echo ".zip" || echo ".tar.xz" )
  - artifacts/ffmpeg-${FFMPEG_BRANCH}-latest-${TARGET}-gpl$( [ "${TARGET:0:3}" = "win" ] && echo ".zip" || echo ".tar.xz" ).sha256
# ==============================================================================
EOF
