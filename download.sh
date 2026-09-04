#!/usr/bin/env bash
# download.sh - Downloads and caches source archives and Git repositories for FFmpeg and libraries

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/util/vars.sh"

CACHE_DIR="${CACHE_DIR:-${BUILD_DIR}/cache}"
mkdir -p "${CACHE_DIR}" "${SRC_DIR}"

download_tarball() {
    local url="$1"
    local filename="$2"
    local dest_dir="$3"

    local cache_file="${CACHE_DIR}/${filename}"
    if [ ! -f "${cache_file}" ]; then
        log_info "Downloading ${filename} from ${url}..."
        curl -fsSL --retry 3 --retry-delay 2 -o "${cache_file}" "${url}"
    else
        log_info "Using cached archive: ${filename}"
    fi

    log_info "Extracting ${filename}..."
    mkdir -p "${dest_dir}"
    if [[ "${filename}" == *.tar.gz ]] || [[ "${filename}" == *.tgz ]]; then
        tar -xzf "${cache_file}" -C "${dest_dir}" --strip-components=1
    elif [[ "${filename}" == *.tar.bz2 ]] || [[ "${filename}" == *.tbz2 ]]; then
        tar -xjf "${cache_file}" -C "${dest_dir}" --strip-components=1
    elif [[ "${filename}" == *.tar.xz ]] || [[ "${filename}" == *.txz ]]; then
        tar -xJf "${cache_file}" -C "${dest_dir}" --strip-components=1
    elif [[ "${filename}" == *.zip ]]; then
        unzip -q -o "${cache_file}" -d "${dest_dir}"
    fi
}

download_git() {
    local repo_url="$1"
    local branch_or_tag="$2"
    local dest_dir="$3"

    if [ -d "${dest_dir}/.git" ]; then
        log_info "Git repo already present at ${dest_dir}, fetching updates..."
        (cd "${dest_dir}" && git fetch --all --tags && git checkout "${branch_or_tag}" && git pull || true)
    else
        log_info "Cloning ${repo_url} (branch: ${branch_or_tag}) into ${dest_dir}..."
        git clone --depth 1 --branch "${branch_or_tag}" "${repo_url}" "${dest_dir}"
    fi
}

# 1. FFmpeg
download_ffmpeg() {
    local branch="${FFMPEG_BRANCH:-master}"
    local ffmpeg_dir="${SRC_DIR}/ffmpeg"
    log_info "Fetching FFmpeg (${branch})..."
    download_git "https://github.com/FFmpeg/FFmpeg.git" "${branch}" "${ffmpeg_dir}"
}

# 2. Dependencies
download_dependencies() {
    log_info "Fetching static library source packages..."

    # Zlib
    download_tarball "https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.gz" "zlib-1.3.1.tar.gz" "${SRC_DIR}/zlib"

    # Bzip2
    download_tarball "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz" "bzip2-1.0.8.tar.gz" "${SRC_DIR}/bzip2"

    # OpenSSL (for secure HTTPS protocol / HLS / DASH stream fetching)
    download_tarball "https://github.com/openssl/openssl/releases/download/openssl-3.3.2/openssl-3.3.2.tar.gz" "openssl-3.3.2.tar.gz" "${SRC_DIR}/openssl"

    # Libxml2 (for DASH MPD manifest support)
    download_tarball "https://download.gnome.org/sources/libxml2/2.12/libxml2-2.12.8.tar.xz" "libxml2-2.12.8.tar.xz" "${SRC_DIR}/libxml2"

    # Ogg & Vorbis
    download_tarball "https://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.gz" "libogg-1.3.5.tar.gz" "${SRC_DIR}/libogg"
    download_tarball "https://downloads.xiph.org/releases/vorbis/libvorbis-1.3.7.tar.gz" "libvorbis-1.3.7.tar.gz" "${SRC_DIR}/libvorbis"

    # Opus
    download_tarball "https://downloads.xiph.org/releases/opus/opus-1.5.2.tar.gz" "opus-1.5.2.tar.gz" "${SRC_DIR}/opus"

    # MP3 Lame
    download_tarball "https://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz" "lame-3.100.tar.gz" "${SRC_DIR}/lame"

    # libvpx (VP8 / VP9)
    download_tarball "https://github.com/webmproject/libvpx/archive/refs/tags/v1.14.1.tar.gz" "libvpx-1.14.1.tar.gz" "${SRC_DIR}/libvpx"

    # x264 (H.264)
    download_git "https://code.videolan.org/videolan/x264.git" "master" "${SRC_DIR}/x264"

    # x265 (H.265 / HEVC)
    download_git "https://bitbucket.org/multicoreware/x265_git.git" "master" "${SRC_DIR}/x265"

    # dav1d (AV1 Decoder)
    download_git "https://code.videolan.org/videolan/dav1d.git" "master" "${SRC_DIR}/dav1d"

    # Freetype, FriBidi, Libass (Subtitles)
    download_tarball "https://download.savannah.gnu.org/releases/freetype/freetype-2.13.3.tar.gz" "freetype-2.13.3.tar.gz" "${SRC_DIR}/freetype"
    download_tarball "https://github.com/fribidi/fribidi/releases/download/v1.0.15/fribidi-1.0.15.tar.xz" "fribidi-1.0.15.tar.xz" "${SRC_DIR}/fribidi"
    download_tarball "https://github.com/libass/libass/releases/download/0.17.2/libass-0.17.2.tar.gz" "libass-0.17.2.tar.gz" "${SRC_DIR}/libass"
}

main() {
    setup_target_env
    download_dependencies
    download_ffmpeg
    log_success "All source dependencies downloaded successfully!"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
