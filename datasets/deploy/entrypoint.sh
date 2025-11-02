#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${APP_CONFIG_PATH:-/app/datasets/deploy/configs/nomad.yaml}"
ENV_PATH="${APP_ENV_PATH:-}"

CMD=(uv run --no-sync -m datasets.app --config "${CONFIG_PATH}")

if [[ -n "${ENV_PATH}" ]]; then
  CMD+=(--env "${ENV_PATH}")
fi

exec "${CMD[@]}"
