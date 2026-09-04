#!/usr/bin/env bash
# scripts.d/40-libvpx.sh - Compile static libvpx (VP8 / VP9)

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libvpx..."
cd "${SRC_DIR}/libvpx"

VPX_TARGET=""
case "${TARGET}" in
    win64)
        VPX_TARGET="x86_64-win64-gcc"
        ;;
    win32)
        VPX_TARGET="x86-win32-gcc"
        ;;
    linux64)
        VPX_TARGET="x86_64-linux-gcc"
        ;;
    linuxarm64)
        VPX_TARGET="arm64-linux-gcc"
        ;;
esac

CROSS="${HOST}-"
if [ "${TARGET}" = "linux64" ]; then
    CROSS=""
fi

CROSS="${CROSS}" ./configure \
    --prefix="${INSTALL_DIR}" \
    --target="${VPX_TARGET}" \
    --enable-static \
    --disable-shared \
    --disable-examples \
    --disable-unit-tests \
    --disable-docs \
    --enable-vp8 \
    --enable-vp9 \
    --enable-vp9-highbitdepth \
    --enable-pic \
    --as=yasm

make -j"${JOBS}"
make install

log_success "libvpx built successfully!"
