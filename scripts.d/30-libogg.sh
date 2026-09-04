#!/usr/bin/env bash
# scripts.d/30-libogg.sh - Compile static libogg

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libogg..."
cd "${SRC_DIR}/libogg"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared

make -j"${JOBS}"
make install

log_success "libogg built successfully!"
