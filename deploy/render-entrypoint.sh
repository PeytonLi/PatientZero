#!/bin/bash
# Render: HydraDB + Patient Zero in one container. Bolt stays on localhost.
set -euo pipefail

mkdir -p /data/store /data/cache
TOKEN_FILE=/data/auth-token
if [ ! -s "$TOKEN_FILE" ]; then
  printf '%s\n' "${HYDRADB_AUTH_TOKEN:-local-development-token-32-bytes}" > "$TOKEN_FILE"
fi

export CLOUD_PROVIDER="${CLOUD_PROVIDER:-local}"
export LOCAL_PATH="${LOCAL_PATH:-/data/store}"
export GRAPH_NAMESPACE="${GRAPH_NAMESPACE:-default}"
export GRAPH_ID="${GRAPH_ID:-default}"
export GRAPH_CELL_ID="${GRAPH_CELL_ID:-cell-0}"
export GRAPH_CELLS="${GRAPH_CELLS:-cell-0}"
export GRAPH_NODE_ID="${GRAPH_NODE_ID:-node-0}"
export GRAPH_BOLT_NODE_ADDRESSES="${GRAPH_BOLT_NODE_ADDRESSES:-node-0=127.0.0.1:7687}"
export GRAPH_ADVERTISED_BOLT_ADDR="${GRAPH_ADVERTISED_BOLT_ADDR:-127.0.0.1:7687}"
export GRAPH_DATA_CACHE_DIR="${GRAPH_DATA_CACHE_DIR:-/data/cache}"
export GRAPH_AUTH_TOKEN_FILE="${GRAPH_AUTH_TOKEN_FILE:-$TOKEN_FILE}"
export GRAPH_ALLOW_PLAINTEXT="${GRAPH_ALLOW_PLAINTEXT:-true}"
export RUST_MIN_STACK="${RUST_MIN_STACK:-33554432}"

export HYDRADB_BOLT_URI="${HYDRADB_BOLT_URI:-bolt://127.0.0.1:7687}"
export HYDRADB_AUTH_TOKEN="${HYDRADB_AUTH_TOKEN:-local-development-token-32-bytes}"
export PATIENT_ZERO_ROOT="${PATIENT_ZERO_ROOT:-/app}"
export PATIENT_ZERO_HOST=0.0.0.0
export PATIENT_ZERO_PORT="${PORT:-${PATIENT_ZERO_PORT:-8080}}"

echo "starting graph-node" >&2
/usr/local/bin/graph-node &

cd /app
exec /opt/pz/bin/python /app/scripts/demo.py
