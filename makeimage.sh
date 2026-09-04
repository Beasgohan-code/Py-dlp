#!/usr/bin/env bash
# makeimage.sh - Builds the target Docker container for compilation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/util/vars.sh"

TARGET="${1:-${TARGET}}"
IMAGE_TAG="ffbuilder-${TARGET}:latest"

log_info "Building Docker image ${IMAGE_TAG} for target ${TARGET}..."

DOCKERFILE="${SCRIPT_DIR}/docker/Dockerfile.${TARGET}"
if [ ! -f "${DOCKERFILE}" ]; then
    log_error "Dockerfile not found: ${DOCKERFILE}"
    exit 1
fi

docker build \
    -t "${IMAGE_TAG}" \
    -f "${DOCKERFILE}" \
    "${SCRIPT_DIR}"

log_success "Docker image ${IMAGE_TAG} built successfully!"
