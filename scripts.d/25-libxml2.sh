#!/usr/bin/env bash
# scripts.d/25-libxml2.sh - Compile static libxml2 for DASH manifest parsing

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libxml2..."
cd "${SRC_DIR}/libxml2"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --without-python \
    --without-lzma \
    --with-zlib="${INSTALL_DIR}" \
    --without-icu \
    --disable-maintainer-mode

make -j"${JOBS}"
make install

log_success "libxml2 built successfully!"
