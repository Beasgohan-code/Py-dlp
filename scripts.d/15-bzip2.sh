#!/usr/bin/env bash
# scripts.d/15-bzip2.sh - Compile static bzip2

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building bzip2..."
cd "${SRC_DIR}/bzip2"

make clean || true
make CC="${CC}" AR="${AR}" RANLIB="${RANLIB}" CFLAGS="${CFLAGS} -D_FILE_OFFSET_BITS=64" libbz2.a -j"${JOBS}"

mkdir -p "${INSTALL_DIR}/include" "${INSTALL_DIR}/lib" "${INSTALL_DIR}/lib/pkgconfig"
cp -f bzlib.h "${INSTALL_DIR}/include/"
cp -f libbz2.a "${INSTALL_DIR}/lib/"

cat << EOF > "${INSTALL_DIR}/lib/pkgconfig/bzip2.pc"
prefix=${INSTALL_DIR}
exec_prefix=\${prefix}
libdir=\${exec_prefix}/lib
includedir=\${prefix}/include

Name: bzip2
Description: bzip2 compression library
Version: 1.0.8
Libs: -L\${libdir} -lbz2
Cflags: -I\${includedir}
EOF

log_success "bzip2 built successfully!"
