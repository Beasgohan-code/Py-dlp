#!/usr/bin/env bash
# scripts.d/35-libmp3lame.sh - Compile static libmp3lame

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libmp3lame..."
cd "${SRC_DIR}/lame"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --disable-frontend \
    --disable-decoder \
    --enable-nasm

make -j"${JOBS}"
make install

log_success "libmp3lame built successfully!"
