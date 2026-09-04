#!/usr/bin/env bash
# scripts.d/60-ffmpeg.sh - Configure, patch, and compile static FFmpeg & FFprobe

set -e
source "${SCRIPT_DIR}/util/vars.sh"

log_info "Configuring and compiling FFmpeg for ${TARGET} (${FFMPEG_BRANCH})..."
cd "${SRC_DIR}/ffmpeg"

# Apply yt-dlp compatibility patches
log_info "Applying yt-dlp compatibility patches..."
for patch in "${PATCHES_DIR}"/*.patch; do
    if [ -f "${patch}" ]; then
        log_info "Applying $(basename "${patch}")..."
        patch -p1 -N -r - < "${patch}" || log_warn "Patch $(basename "${patch}") was skipped or already applied."
    fi
done

EXTRA_FFMPEG_FLAGS=()

# Cross-compilation settings
if [ "${TARGET}" = "win64" ]; then
    EXTRA_FFMPEG_FLAGS+=(
        --arch=x86_64
        --target-os=mingw32
        --cross-prefix=x86_64-w64-mingw32-
        --enable-w32threads
    )
elif [ "${TARGET}" = "win32" ]; then
    EXTRA_FFMPEG_FLAGS+=(
        --arch=i686
        --target-os=mingw32
        --cross-prefix=i686-w64-mingw32-
        --enable-w32threads
    )
elif [ "${TARGET}" = "linuxarm64" ]; then
    EXTRA_FFMPEG_FLAGS+=(
        --arch=aarch64
        --target-os=linux
        --cross-prefix=aarch64-linux-gnu-
        --enable-pthreads
    )
else
    EXTRA_FFMPEG_FLAGS+=(
        --arch=x86_64
        --target-os=linux
        --enable-pthreads
    )
fi

./configure \
    --prefix="${INSTALL_DIR}" \
    --pkg-config-flags="--static" \
    --extra-cflags="${CFLAGS} -I${INSTALL_DIR}/include" \
    --extra-cxxflags="${CXXFLAGS} -I${INSTALL_DIR}/include" \
    --extra-ldflags="${LDFLAGS} -L${INSTALL_DIR}/lib" \
    --enable-static \
    --disable-shared \
    --enable-gpl \
    --enable-version3 \
    --enable-nonfree \
    --disable-doc \
    --disable-ffplay \
    --enable-ffmpeg \
    --enable-ffprobe \
    --enable-openssl \
    --enable-libxml2 \
    --enable-libvpx \
    --enable-libopus \
    --enable-libvorbis \
    --enable-libmp3lame \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libdav1d \
    --enable-libass \
    --enable-libfreetype \
    --enable-libfribidi \
    --enable-zlib \
    --enable-bzlib \
    --enable-swscale \
    --enable-swresample \
    --enable-avformat \
    --enable-avcodec \
    --enable-avutil \
    --enable-avfilter \
    --enable-postproc \
    --enable-protocol=file \
    --enable-protocol=pipe \
    --enable-protocol=http \
    --enable-protocol=https \
    --enable-protocol=tcp \
    --enable-protocol=tls \
    --enable-protocol=crypto \
    --enable-protocol=hls \
    --enable-protocol=concat \
    --enable-demuxer=dash \
    --enable-demuxer=hls \
    --enable-demuxer=flv \
    "${EXTRA_FFMPEG_FLAGS[@]}"

log_info "Compiling FFmpeg and FFprobe..."
make -j"${JOBS}"

log_info "Installing binaries to ${INSTALL_DIR}..."
make install

# Strip binaries to minimize size
log_info "Stripping debug symbols from binaries..."
${STRIP} "${INSTALL_DIR}/bin/ffmpeg${EXE_EXT}"
${STRIP} "${INSTALL_DIR}/bin/ffprobe${EXE_EXT}"

log_success "FFmpeg and FFprobe compiled and stripped successfully!"
