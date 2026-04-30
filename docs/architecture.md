# Sentinel Architecture

Sentinel is split into a VPS agent, a local dashboard backend, and a React frontend.

The agent is read-only by default and exposes Docker, system, and health-check data through authenticated HTTP endpoints. The recommended deployment is HTTP over Tailscale or another private network, with the agent bound to a private interface.

The dashboard backend stores server configurations, encrypted agent API keys, metric snapshots, alert history, health checks, notification settings, audit events, action logs, and backup metadata in SQLite. It polls configured agents on a schedule and broadcasts state changes to the browser over WebSockets.

The frontend is an operational dashboard for personal infrastructure: overview cards, server and container tables, log viewing, charts, alerts, health checks, notifications, settings, and backups.

