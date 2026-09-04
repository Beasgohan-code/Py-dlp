#!/usr/bin/env bash
# scripts.d/46-libx265.sh - Compile static libx265 (HEVC / H.265)

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building libx265..."
cd "${SRC_DIR}/x265/source"

rm -rf build && mkdir build && cd build

CMAKE_CROSS_FLAGS=""
if [ "${TARGET}" = "win64" ] || [ "${TARGET}" = "win32" ] || [ "${TARGET}" = "linuxarm64" ]; then
    CMAKE_CROSS_FLAGS="-DCMAKE_SYSTEM_NAME=${CMAKE_SYSTEM_NAME} -DCMAKE_C_COMPILER=${CC} -DCMAKE_CXX_COMPILER=${CXX} -DCMAKE_RC_COMPILER=${WINDRES:-}"
fi

cmake .. \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
    -DENABLE_SHARED=OFF \
    -DENABLE_CLI=OFF \
    -DENABLE_PIC=ON \
    ${CMAKE_CROSS_FLAGS}

make -j"${JOBS}"
make install

# Fix pkgconfig file if needed
sed -i.bak 's/-lgcc_s//g' "${INSTALL_DIR}/lib/pkgconfig/x265.pc" 2>/dev/null || true

log_success "libx265 built successfully!"
