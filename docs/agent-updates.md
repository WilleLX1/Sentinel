# Agent Update Automation

Use the agent scripts on each Linux server that runs `sentinel-agent`.

## One-Time Setup

From the Sentinel repository on the VPS or Raspberry Pi:

```bash
cd ~/Sentinel
bash scripts/configure-agent.sh
```

The script detects the server's Tailscale IPv4 address and writes `docker-compose.override.yml`.
Docker Compose automatically applies this file, so future commands can use plain `docker compose up ...` without losing the Tailscale port binding.

Start or reapply the agent:

```bash
bash scripts/update-agent.sh
```

## Automatic Updates

Install a systemd timer:

```bash
sudo bash scripts/install-agent-autoupdate.sh
```

Defaults:

- Runs after boot.
- Runs every 15 minutes.
- Performs `git pull --ff-only`.
- Rewrites `docker-compose.override.yml`.
- Rebuilds and recreates `sentinel-agent`.
- Verifies local `/api/ping`.

Customize interval:

```bash
sudo SENTINEL_UPDATE_INTERVAL=1h bash scripts/install-agent-autoupdate.sh
```

Skip git pull during an update:

```bash
SENTINEL_SKIP_GIT_PULL=1 bash scripts/update-agent.sh
```

Use an explicit bind IP instead of auto-detecting Tailscale:

```bash
SENTINEL_BIND_IP=100.x.x.x bash scripts/configure-agent.sh
```

## Useful Checks

```bash
docker port sentinel-agent
docker exec sentinel-agent printenv | grep SENTINEL
systemctl list-timers | grep sentinel-agent-update
journalctl -u sentinel-agent-update.service -n 100 --no-pager
```

