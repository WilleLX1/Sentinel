#!/usr/bin/env bash
set -eu

if [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "Run this installer with sudo/root."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_PATH="/etc/systemd/system/sentinel-agent-update.service"
TIMER_PATH="/etc/systemd/system/sentinel-agent-update.timer"
RUN_AS_USER="${SENTINEL_UPDATE_USER:-$(stat -c '%U' "$ROOT_DIR")}"
INTERVAL="${SENTINEL_UPDATE_INTERVAL:-15min}"

cat > "$SERVICE_PATH" <<UNIT
[Unit]
Description=Update and reapply Sentinel agent deployment
Wants=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
User=${RUN_AS_USER}
WorkingDirectory=${ROOT_DIR}
ExecStart=/usr/bin/env bash ${ROOT_DIR}/scripts/update-agent.sh
UNIT

cat > "$TIMER_PATH" <<UNIT
[Unit]
Description=Run Sentinel agent update periodically

[Timer]
OnBootSec=2min
OnUnitActiveSec=${INTERVAL}
Persistent=true

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now sentinel-agent-update.timer

printf '%s\n' "Installed sentinel-agent-update.timer"
printf '%s\n' "Status:"
systemctl --no-pager status sentinel-agent-update.timer || true

