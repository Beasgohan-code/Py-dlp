#!/usr/bin/env bash
# scripts.d/20-openssl.sh - Compile static OpenSSL for HTTPS/TLS streaming

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Building OpenSSL for ${TARGET}..."
cd "${SRC_DIR}/openssl"

OPENSSL_TARGET=""
case "${TARGET}" in
    win64)
        OPENSSL_TARGET="mingw64"
        ;;
    win32)
        OPENSSL_TARGET="mingw"
        ;;
    linux64)
        OPENSSL_TARGET="linux-x86_64"
        ;;
    linuxarm64)
        OPENSSL_TARGET="linux-aarch64"
        ;;
esac

./Configure \
    "${OPENSSL_TARGET}" \
    --prefix="${INSTALL_DIR}" \
    --openssldir="${INSTALL_DIR}/ssl" \
    no-shared \
    no-tests \
    no-unit-test \
    no-dynamic-engine \
    --cross-compile-prefix="${HOST}-" \
    ${CFLAGS}

make -j"${JOBS}"
make install_sw

log_success "OpenSSL built successfully!"
