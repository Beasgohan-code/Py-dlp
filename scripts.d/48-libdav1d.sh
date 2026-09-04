#!/usr/bin/env bash
# scripts.d/48-libdav1d.sh - Compile static libdav1d (AV1 Decoder)

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libdav1d..."
cd "${SRC_DIR}/dav1d"

rm -rf build && mkdir build

MESON_CROSS=""
if [ "${TARGET}" = "win64" ] || [ "${TARGET}" = "win32" ] || [ "${TARGET}" = "linuxarm64" ]; then
    cat << EOF > cross_file.meson
[binaries]
c = '${CC}'
cpp = '${CXX}'
ar = '${AR}'
ranlib = '${RANLIB}'
strip = '${STRIP}'
windres = '${WINDRES:-windres}'

[host_machine]
system = '${OS}'
cpu_family = '${ARCH}'
cpu = '${ARCH}'
endian = 'little'
EOF
    MESON_CROSS="--cross-file cross_file.meson"
fi

meson setup build \
    --prefix="${INSTALL_DIR}" \
    --default-library=static \
    --buildtype=release \
    -Denable_tools=false \
    -Denable_tests=false \
    ${MESON_CROSS}

ninja -C build -j"${JOBS}"
ninja -C build install

log_success "libdav1d built successfully!"
