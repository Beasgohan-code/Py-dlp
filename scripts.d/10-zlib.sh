#!/usr/bin/env bash
# scripts.d/10-zlib.sh - Compile static zlib

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building zlib..."
cd "${SRC_DIR}/zlib"

if [ "${TARGET}" = "win64" ] || [ "${TARGET}" = "win32" ]; then
    make -f win32/Makefile.gcc PREFIX="${HOST}-" -j"${JOBS}"
    make -f win32/Makefile.gcc install INCLUDE_PATH="${INSTALL_DIR}/include" LIBRARY_PATH="${INSTALL_DIR}/lib" BINARY_PATH="${INSTALL_DIR}/bin"
    
    # Generate pkg-config file for Windows
    mkdir -p "${INSTALL_DIR}/lib/pkgconfig"
    cat << EOF > "${INSTALL_DIR}/lib/pkgconfig/zlib.pc"
prefix=${INSTALL_DIR}
exec_prefix=\${prefix}
libdir=\${exec_prefix}/lib
sharedlibdir=\${libdir}
includedir=\${prefix}/include

Name: zlib
Description: zlib compression library
Version: 1.3.1
Requires:
Libs: -L\${libdir} -lz
Cflags: -I\${includedir}
EOF
else
    CHOST="${HOST}" ./configure --prefix="${INSTALL_DIR}" --static
    make -j"${JOBS}"
    make install
fi

log_success "zlib built successfully!"
