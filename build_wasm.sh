#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="bhoogol-wasm"
CONTAINER_NAME="bhoogol-wasm-server"

echo "==> Building WASM Docker image..."
docker build -t "$IMAGE_NAME" .

echo "==> Stopping any previous container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "==> Starting server on http://localhost:8080"
docker run -d --name "$CONTAINER_NAME" -p 8080:8080 "$IMAGE_NAME"

echo "==> Done!  Open http://localhost:8080 in your browser."
