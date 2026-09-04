#!/usr/bin/env bash
# scripts.d/31-libvorbis.sh - Compile static libvorbis

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libvorbis..."
cd "${SRC_DIR}/libvorbis"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --with-ogg="${INSTALL_DIR}"

make -j"${JOBS}"
make install

log_success "libvorbis built successfully!"
