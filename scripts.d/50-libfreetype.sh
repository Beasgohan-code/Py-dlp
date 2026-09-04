#!/usr/bin/env bash
# scripts.d/50-libfreetype.sh - Compile static libfreetype

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libfreetype..."
cd "${SRC_DIR}/freetype"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --with-zlib=yes \
    --with-bzip2=yes \
    --with-png=no \
    --with-harfbuzz=no \
    --with-brotli=no

make -j"${JOBS}"
make install

log_success "libfreetype built successfully!"
