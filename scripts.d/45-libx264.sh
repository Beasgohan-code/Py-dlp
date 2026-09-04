#!/usr/bin/env bash
# scripts.d/45-libx264.sh - Compile static libx264 (H.264)

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libx264..."
cd "${SRC_DIR}/x264"

EXTRA_FLAGS=""
if [ "${TARGET}" = "win64" ] || [ "${TARGET}" = "win32" ]; then
    EXTRA_FLAGS="--enable-win32thread"
fi

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --cross-prefix="${HOST}-" \
    --enable-static \
    --disable-cli \
    --enable-pic \
    --disable-lavf \
    --disable-ffms \
    --disable-opencl \
    ${EXTRA_FLAGS}

make -j"${JOBS}"
make install

log_success "libx264 built successfully!"
