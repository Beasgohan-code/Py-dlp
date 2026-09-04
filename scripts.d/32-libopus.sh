#!/usr/bin/env bash
# scripts.d/32-libopus.sh - Compile static libopus

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libopus..."
cd "${SRC_DIR}/opus"

./configure \
    --prefix="${INSTALL_DIR}" \
    --host="${HOST}" \
    --enable-static \
    --disable-shared \
    --disable-extra-programs \
    --disable-doc

make -j"${JOBS}"
make install

log_success "libopus built successfully!"
