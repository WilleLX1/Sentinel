#!/usr/bin/env bash
set -eu

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log() {
  printf '%s\n' "$*"
}

read_env_value() {
  key="$1"
  default_value="$2"
  if [ -f .env ]; then
    value="$(awk -F= -v key="$key" '$1 == key {print substr($0, length(key) + 2)}' .env | tail -n 1)"
    if [ -n "$value" ]; then
      printf '%s' "$value"
      return
    fi
  fi
  printf '%s' "$default_value"
}

if [ "${SENTINEL_SKIP_GIT_PULL:-0}" != "1" ] && [ -d .git ]; then
  current_branch="$(git branch --show-current 2>/dev/null || true)"
  if [ -n "$current_branch" ]; then
    log "Fetching latest changes for ${current_branch}"
    git fetch --prune
    git pull --ff-only
  else
    log "Skipping git pull because this checkout is not on a branch"
  fi
fi

bash scripts/configure-agent.sh

log "Building and recreating sentinel-agent"
docker compose up -d --build --force-recreate sentinel-agent

AGENT_PORT="${AGENT_PORT:-$(read_env_value AGENT_PORT 8443)}"
API_KEY="${SENTINEL_API_KEY:-$(read_env_value SENTINEL_API_KEY "")}"

log "Current published ports:"
docker port sentinel-agent || true

if [ -n "$API_KEY" ] && command -v curl >/dev/null 2>&1; then
  log "Checking local agent ping"
  curl -fsS \
    -H "Authorization: Bearer ${API_KEY}" \
    "http://127.0.0.1:${AGENT_PORT}/api/ping" >/dev/null
  log "Agent ping OK"
else
  log "Skipping ping check because curl or SENTINEL_API_KEY is unavailable"
fi

log "Sentinel agent update complete"

