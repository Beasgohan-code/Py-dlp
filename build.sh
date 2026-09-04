#!/usr/bin/env bash
# build.sh - Master build orchestrator for static FFmpeg builds

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/util/vars.sh"

export TARGET="${1:-${TARGET}}"
export FFMPEG_BRANCH="${2:-${FFMPEG_BRANCH}}"

log_info "=========================================================="
log_info "Starting FFmpeg Static Build for yt-dlp"
log_info "Target:        ${TARGET}"
log_info "FFmpeg Branch: ${FFMPEG_BRANCH}"
log_info "Build Dir:     ${BUILD_DIR}"
log_info "Install Dir:   ${INSTALL_DIR}"
log_info "Artifacts Dir: ${ARTIFACTS_DIR}"
log_info "=========================================================="

setup_target_env

# 1. Download source packages
"${SCRIPT_DIR}/download.sh"

# 2. Run all dependency compilation scripts in order
for script in "${SCRIPT_DIR}"/scripts.d/[0-5]*.sh; do
    if [ -f "${script}" ]; then
        log_info "Executing library build: $(basename "${script}")..."
        bash "${script}"
    fi
done

# 3. Configure, patch, and build FFmpeg
bash "${SCRIPT_DIR}/scripts.d/60-ffmpeg.sh"

# 4. Package binaries and generate checksums
bash "${SCRIPT_DIR}/package.sh"

log_success "Build and packaging completed successfully!"
