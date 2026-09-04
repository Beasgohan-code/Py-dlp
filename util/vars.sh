#!/usr/bin/env bash
# util/vars.sh - Common environment variables and configuration for FFmpeg builds

set -e

# Target Architectures: win64, win32, linux64, linuxarm64
TARGET="${TARGET:-linux64}"
FFMPEG_BRANCH="${FFMPEG_BRANCH:-master}"
BUILD_DIR="${BUILD_DIR:-/build}"
INSTALL_DIR="${INSTALL_DIR:-/opt/ffmpeg-static}"
SRC_DIR="${SRC_DIR:-/build/src}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-/build/artifacts}"
PATCHES_DIR="${PATCHES_DIR:-/patches}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 4)}"

# Formatting & Colors
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}${BOLD}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}${BOLD}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}${BOLD}[ERROR]${NC} $*" >&2
}

# Setup Target-Specific Cross-Compilation Environment
setup_target_env() {
    case "${TARGET}" in
        win64)
            export HOST="x86_64-w64-mingw32"
            export ARCH="x86_64"
            export OS="mingw32"
            export EXE_EXT=".exe"
            export ARCHIVE_EXT=".zip"
            export CC="${HOST}-gcc"
            export CXX="${HOST}-g++"
            export AR="${HOST}-ar"
            export RANLIB="${HOST}-ranlib"
            export STRIP="${HOST}-strip"
            export WINDRES="${HOST}-windres"
            export CFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export CXXFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export LDFLAGS="-static -static-libgcc -static-libstdc++ -Wl,-Bstatic"
            export PKG_CONFIG_LIBDIR="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG_PATH="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG="pkg-config --static"
            export CMAKE_SYSTEM_NAME="Windows"
            ;;
        win32)
            export HOST="i686-w64-mingw32"
            export ARCH="i686"
            export OS="mingw32"
            export EXE_EXT=".exe"
            export ARCHIVE_EXT=".zip"
            export CC="${HOST}-gcc"
            export CXX="${HOST}-g++"
            export AR="${HOST}-ar"
            export RANLIB="${HOST}-ranlib"
            export STRIP="${HOST}-strip"
            export WINDRES="${HOST}-windres"
            export CFLAGS="-O3 -march=i686 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export CXXFLAGS="-O3 -march=i686 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export LDFLAGS="-static -static-libgcc -static-libstdc++ -Wl,-Bstatic"
            export PKG_CONFIG_LIBDIR="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG_PATH="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG="pkg-config --static"
            export CMAKE_SYSTEM_NAME="Windows"
            ;;
        linux64)
            export HOST="x86_64-linux-gnu"
            export ARCH="x86_64"
            export OS="linux"
            export EXE_EXT=""
            export ARCHIVE_EXT=".tar.xz"
            export CC="gcc"
            export CXX="g++"
            export AR="ar"
            export RANLIB="ranlib"
            export STRIP="strip"
            export CFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export CXXFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export LDFLAGS="-static -static-libgcc -static-libstdc++ -Wl,-Bstatic"
            export PKG_CONFIG_LIBDIR="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG_PATH="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG="pkg-config --static"
            export CMAKE_SYSTEM_NAME="Linux"
            ;;
        linuxarm64)
            export HOST="aarch64-linux-gnu"
            export ARCH="aarch64"
            export OS="linux"
            export EXE_EXT=""
            export ARCHIVE_EXT=".tar.xz"
            export CC="${HOST}-gcc"
            export CXX="${HOST}-g++"
            export AR="${HOST}-ar"
            export RANLIB="${HOST}-ranlib"
            export STRIP="${HOST}-strip"
            export CFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export CXXFLAGS="-O3 -fstack-protector-strong -D_FORTIFY_SOURCE=2"
            export LDFLAGS="-static -static-libgcc -static-libstdc++ -Wl,-Bstatic"
            export PKG_CONFIG_LIBDIR="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG_PATH="${INSTALL_DIR}/lib/pkgconfig"
            export PKG_CONFIG="pkg-config --static"
            export CMAKE_SYSTEM_NAME="Linux"
            ;;
        *)
            log_error "Unsupported target architecture: ${TARGET}"
            exit 1
            ;;
    esac

    export PATH="${INSTALL_DIR}/bin:${PATH}"
    export LD_LIBRARY_PATH="${INSTALL_DIR}/lib:${LD_LIBRARY_PATH}"
}
