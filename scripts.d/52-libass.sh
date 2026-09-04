#!/usr/bin/env bash
# scripts.d/52-libass.sh - Compile static libass

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libass..."
cd "${SRC_DIR}/libass"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --disable-fontconfig \
    --disable-require-system-font-provider

make -j"${JOBS}"
make install

log_success "libass built successfully!"
