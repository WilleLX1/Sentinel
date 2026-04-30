# Sentinel

**Sentinel** is a self-hosted Docker and server monitoring system designed for small VPS setups, homelabs, and personal infrastructure.

The idea is simple: run a lightweight monitoring agent on your VPS, then connect to it from a local dashboard on your own PC. The dashboard shows Docker container status, logs, system usage, disk health, exposed ports, alerts, and historical metrics.

This project is meant to be a lightweight alternative to tools like Portainer, Uptime Kuma, Netdata, and Datadog, but built specifically for personal infrastructure where you want full control and a clean custom dashboard.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Core Idea](#core-idea)
* [Example Use Case](#example-use-case)
* [Main Features](#main-features)
* [Architecture](#architecture)
* [Components](#components)
* [Security Model](#security-model)
* [Recommended Tech Stack](#recommended-tech-stack)
* [Project Structure](#project-structure)
* [Agent Design](#agent-design)
* [Dashboard Design](#dashboard-design)
* [API Design](#api-design)
* [Database Design](#database-design)
* [Installation Guide](#installation-guide)
* [Docker Compose Setup](#docker-compose-setup)
* [Environment Variables](#environment-variables)
* [Running the Agent](#running-the-agent)
* [Running the Local Dashboard](#running-the-local-dashboard)
* [Using Tailscale or WireGuard](#using-tailscale-or-wireguard)
* [Alerting System](#alerting-system)
* [Logging System](#logging-system)
* [Metrics Collection](#metrics-collection)
* [Roadmap](#roadmap)
* [Security Notes](#security-notes)
* [Development Notes](#development-notes)
* [Future Ideas](#future-ideas)
* [License](#license)

---

## Project Overview

Sentinel is a monitoring system split into two main parts:

1. **VPS Agent**
   A small API service running on the VPS. It collects Docker and system information directly from the server.

2. **Local Dashboard**
   A web interface running locally on your PC. It calls the VPS Agent when you open the dashboard and displays status, logs, metrics, and alerts.

The system is designed to start as a read-only monitoring platform. Later, it can optionally support safe remote management actions like restarting containers, pulling images, or triggering backups.

---

## Core Idea

The agent runs on the VPS and has access to the local Docker Engine through the Docker socket.

The dashboard runs on your own computer and connects to the agent through a secure API.

```text
Your PC
└── Local Dashboard
    └── Calls secure HTTPS/private API
        └── Sentinel Agent
            ├── Docker Engine
            ├── Docker Containers
            ├── System Metrics
            ├── Logs
            └── Health Checks
```

The dashboard does not need to run publicly. It can run on `localhost` and only fetch data when you open it.

---

## Example Use Case

Imagine you have a VPS running two Docker applications:

* A Flask web app
* An Nginx reverse proxy

You want to quickly see:

* Are both containers running?
* Is one of them unhealthy?
* How much RAM is each container using?
* Are there errors in the logs?
* Is the disk almost full?
* Has a container restarted recently?
* Are ports `80` and `443` open?
* Is the SSL certificate expiring soon?

Instead of SSHing into the server and manually running commands like:

```bash
docker ps
docker logs app-name
docker stats
df -h
free -m
systemctl status nginx
```

You open one dashboard and see everything in one place.

---

## Main Features

### Docker Monitoring

Sentinel should be able to show:

* Running containers
* Stopped containers
* Unhealthy containers
* Container image names
* Container IDs
* Restart counts
* Container uptime
* Exposed ports
* Published ports
* Docker networks
* Docker volumes
* Docker image list
* Container labels
* Container environment summary, with secrets hidden
* Health check status
* Last container error

---

### Container Logs

The dashboard should allow you to view logs for each container.

Planned log features:

* Last 100 log lines
* Last 500 log lines
* Live log streaming
* Search inside logs
* Highlight errors and warnings
* Filter by timestamp
* Filter by keyword
* Download logs
* Detect repeated errors

Example:

```text
[INFO]  Server started on port 5000
[INFO]  Connected to database
[ERROR] Permission denied: /app/activity.log
[WARN]  Health check failed once
```

---

### System Monitoring

The agent should collect system-level information from the VPS.

Examples:

* CPU usage
* RAM usage
* Swap usage
* Disk usage
* Disk free space
* Network traffic
* Server uptime
* Load average
* Running processes summary
* Kernel version
* Hostname
* Operating system
* Public/private IP addresses

Example dashboard card:

```text
william-vps-01
Status: Online
CPU: 14%
RAM: 51%
Disk: 73%
Uptime: 9 days, 4 hours
```

---

### Health Checks

The system should support health checks for applications.

Possible health checks:

* HTTP status code check
* Response time check
* Docker health check status
* Port open check
* SSL certificate expiry check
* Disk usage threshold
* Container restart threshold
* Container memory threshold
* Nginx config test

Example:

```text
muf-site
Container: running
Health: healthy
HTTP: 200 OK
Response time: 84 ms
SSL expires in: 61 days
```

---

### Alerts

Sentinel should detect problems and display alerts.

Example alerts:

* Container stopped
* Container unhealthy
* Container restarted too many times
* Disk usage above 85%
* RAM usage above 90%
* CPU usage above 95% for several minutes
* SSL certificate expires soon
* App returns HTTP 500
* App response time is too high
* Docker daemon unreachable
* Agent offline
* New container appeared
* Container image changed
* Suspicious exposed port detected

Example alert:

```text
Severity: Critical
Title: Container stopped
Message: Container "muf-site" stopped unexpectedly at 18:42.
Server: william-vps-01
```

---

### Historical Metrics

The local dashboard can store snapshots over time.

Examples:

* CPU history
* RAM history
* Disk usage history
* Container status history
* Container restart history
* Response time history
* Alert history

This allows graphs such as:

* CPU usage over 24 hours
* RAM usage over 7 days
* Disk growth over 30 days
* Container restarts per week
* Average response time per app

---

## Architecture

There are two main architecture options.

---

### Option A: Pull-Based Monitoring

This is the recommended first version.

```text
Local Dashboard ---> VPS Agent ---> Docker/System Info
```

The dashboard calls the VPS Agent when needed.

Advantages:

* Simple to build
* No need for the VPS to know your home IP
* Good for manual monitoring
* Easier authentication model
* Works well with Tailscale or WireGuard

Disadvantages:

* No monitoring while the dashboard is not running
* Historical data is only collected when the local backend is running
* Alerts are not sent unless the dashboard/backend is active

---

### Option B: Push-Based Monitoring

Possible later version.

```text
VPS Agent ---> Central Collector ---> Dashboard
```

The VPS Agent regularly sends data to a central collector.

Advantages:

* Better historical metrics
* Better alerting
* Works even when dashboard is not open
* Can support many servers more easily

Disadvantages:

* More complex
* Requires a reachable collector
* More moving parts
* More security considerations

---

## Components

### 1. VPS Agent

The VPS Agent is a small FastAPI application running inside Docker.

Responsibilities:

* Authenticate dashboard requests
* Read Docker container information
* Read Docker logs
* Read Docker stats
* Read system metrics
* Run health checks
* Return JSON responses
* Optionally stream logs over WebSockets

The agent should be read-only in the first version.

---

### 2. Local Dashboard Backend

The local backend runs on your PC.

Responsibilities:

* Store server configurations
* Store encrypted API keys or tokens
* Poll agent endpoints
* Store historical snapshots
* Generate alerts
* Serve the frontend
* Provide WebSocket updates to the browser

---

### 3. Frontend Dashboard

The frontend is the visual interface.

Responsibilities:

* Display all monitored servers
* Display Docker container status
* Display logs
* Display metrics graphs
* Display alerts
* Allow server settings management
* Show live updates

---

## Security Model

This project must be treated as an administrative tool.

The VPS Agent can read Docker data from the host. Even if the Docker socket is mounted read-only, access to Docker metadata and logs can reveal sensitive information.

Minimum security requirements:

* API key authentication
* HTTPS or private network access
* Do not expose the agent publicly without protection
* Use firewall rules
* Hide sensitive environment variables
* Limit request rate
* Log all requests
* Do not include secrets in API responses
* Run the dashboard locally
* Prefer Tailscale or WireGuard for access

Recommended secure design:

```text
PC Dashboard <-- private VPN --> VPS Agent
```

Avoid this design unless properly protected:

```text
Internet ---> Public VPS Agent API
```

---

## Recommended Tech Stack

### VPS Agent

Recommended:

* Python
* FastAPI
* Docker SDK for Python
* psutil
* Uvicorn
* Pydantic

Optional:

* aiohttp
* httpx
* websockets
* cryptography

---

### Local Dashboard Backend

Recommended:

* Python
* FastAPI
* SQLite
* SQLModel or SQLAlchemy
* APScheduler for periodic polling
* WebSockets for live updates

---

### Frontend

Recommended:

* React
* Vite
* TypeScript
* Tailwind CSS
* Recharts
* Lucide icons

Alternative simple stack:

* FastAPI
* Jinja2
* HTMX
* Alpine.js

---

## Project Structure

Suggested monorepo layout:

```text
sentinel/
├── README.md
├── docker-compose.yml
├── .env.example
├── agent/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── auth.py
│       ├── docker_client.py
│       ├── system_stats.py
│       ├── health_checks.py
│       ├── security.py
│       └── routes/
│           ├── ping.py
│           ├── system.py
│           ├── containers.py
│           ├── logs.py
│           ├── images.py
│           ├── volumes.py
│           └── networks.py
├── dashboard-backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── polling.py
│       ├── alerts.py
│       ├── encryption.py
│       └── routes/
│           ├── servers.py
│           ├── containers.py
│           ├── metrics.py
│           ├── alerts.py
│           └── settings.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Servers.tsx
│       │   ├── ServerDetail.tsx
│       │   ├── Containers.tsx
│       │   ├── ContainerDetail.tsx
│       │   ├── Logs.tsx
│       │   ├── Alerts.tsx
│       │   └── Settings.tsx
│       ├── components/
│       │   ├── ServerCard.tsx
│       │   ├── ContainerTable.tsx
│       │   ├── MetricCard.tsx
│       │   ├── LogViewer.tsx
│       │   ├── AlertList.tsx
│       │   └── StatusBadge.tsx
│       └── charts/
│           ├── CpuChart.tsx
│           ├── MemoryChart.tsx
│           ├── DiskChart.tsx
│           └── ResponseTimeChart.tsx
└── docs/
    ├── architecture.md
    ├── api.md
    ├── security.md
    └── development.md
```

---

## Agent Design

The agent should expose a small REST API.

The first version should avoid destructive actions.

Allowed in MVP:

* Read container status
* Read logs
* Read stats
* Read system metrics
* Read images
* Read networks
* Read volumes
* Run simple health checks

Not included in MVP:

* Stop containers
* Start containers
* Restart containers
* Delete containers
* Delete images
* Execute commands inside containers
* Modify Docker Compose stacks

This keeps the first version safer.

---

## Dashboard Design

The dashboard should be clean and fast.

Suggested pages:

```text
Dashboard
├── Overview
├── Servers
├── Containers
├── Logs
├── Metrics
├── Alerts
├── Health Checks
└── Settings
```

---

### Overview Page

The overview page should show all monitored servers.

Example:

```text
Sentinel

Servers
--------------------------------------------------
william-vps-01     Online     2 running     0 alerts
home-server-01     Online     6 running     1 warning
raspberrypi-01     Offline    unknown       critical
--------------------------------------------------
```

Useful cards:

* Total servers
* Online servers
* Offline servers
* Running containers
* Unhealthy containers
* Active alerts
* Disk warnings
* SSL warnings

---

### Server Detail Page

Example:

```text
william-vps-01

Status: Online
OS: Debian 12
Docker: Running
Uptime: 9 days, 4 hours
CPU: 14%
RAM: 51%
Disk: 73%

Containers:
- nginx-proxy       running     healthy
- muf-site          running     healthy
- old-test-app      exited      none
```

---

### Container Detail Page

Example:

```text
Container: muf-site

Status: running
Health: healthy
Image: muf-site-web:latest
Ports: 443 -> 5000
Restart count: 0
CPU: 3.4%
RAM: 182 MB
Created: 2026-04-29 18:42
Started: 2026-04-29 18:43

Actions:
[View Logs]
[View Metrics]
[Open App]
```

---

## API Design

All protected endpoints should require an authorization header:

```http
Authorization: Bearer <API_KEY>
```

---

### Agent API Endpoints

#### Ping

```http
GET /api/ping
```

Example response:

```json
{
  "status": "ok",
  "agent": "sentinel-agent",
  "version": "0.1.0",
  "server_name": "william-vps-01"
}
```

---

#### System Overview

```http
GET /api/system
```

Example response:

```json
{
  "hostname": "william-vps-01",
  "os": "Debian 12",
  "uptime_seconds": 794300,
  "cpu_percent": 14.2,
  "memory": {
    "total_mb": 2048,
    "used_mb": 1044,
    "percent": 51.0
  },
  "disk": {
    "total_gb": 40,
    "used_gb": 29,
    "percent": 72.5
  }
}
```

---

#### Docker Overview

```http
GET /api/docker
```

Example response:

```json
{
  "docker_available": true,
  "containers_total": 3,
  "containers_running": 2,
  "containers_stopped": 1,
  "containers_unhealthy": 0,
  "images_total": 8,
  "volumes_total": 4,
  "networks_total": 3
}
```

---

#### List Containers

```http
GET /api/docker/containers
```

Example response:

```json
[
  {
    "id": "abc123",
    "short_id": "abc123",
    "name": "muf-site",
    "image": "muf-site-web:latest",
    "status": "running",
    "health": "healthy",
    "created": "2026-04-29T18:42:00Z",
    "ports": [
      {
        "container_port": 5000,
        "host_port": 443,
        "protocol": "tcp"
      }
    ],
    "restart_count": 0
  }
]
```

---

#### Container Detail

```http
GET /api/docker/containers/{container_id_or_name}
```

Example response:

```json
{
  "id": "abc123",
  "name": "muf-site",
  "image": "muf-site-web:latest",
  "status": "running",
  "health": "healthy",
  "restart_count": 0,
  "created": "2026-04-29T18:42:00Z",
  "started_at": "2026-04-29T18:43:00Z",
  "networks": ["proxy"],
  "volumes": ["muf_data"],
  "ports": [
    {
      "container_port": 5000,
      "host_port": 443,
      "protocol": "tcp"
    }
  ]
}
```

---

#### Container Logs

```http
GET /api/docker/containers/{container_id_or_name}/logs?lines=100
```

Example response:

```json
{
  "container": "muf-site",
  "lines": [
    "[INFO] Server started",
    "[INFO] Connected to database",
    "[ERROR] Permission denied: /app/activity.log"
  ]
}
```

---

#### Container Stats

```http
GET /api/docker/containers/{container_id_or_name}/stats
```

Example response:

```json
{
  "container": "muf-site",
  "cpu_percent": 3.4,
  "memory_usage_mb": 182.7,
  "memory_limit_mb": 2048,
  "memory_percent": 8.9,
  "network_rx_mb": 120.4,
  "network_tx_mb": 32.8
}
```

---

#### Images

```http
GET /api/docker/images
```

Example response:

```json
[
  {
    "id": "sha256:123",
    "tags": ["muf-site-web:latest"],
    "size_mb": 420.5,
    "created": "2026-04-28T12:00:00Z"
  }
]
```

---

#### Networks

```http
GET /api/docker/networks
```

Example response:

```json
[
  {
    "id": "net123",
    "name": "proxy",
    "driver": "bridge",
    "containers": ["nginx-proxy", "muf-site"]
  }
]
```

---

#### Volumes

```http
GET /api/docker/volumes
```

Example response:

```json
[
  {
    "name": "muf_data",
    "driver": "local",
    "mountpoint": "/var/lib/docker/volumes/muf_data/_data"
  }
]
```

---

## Database Design

The local dashboard should store server configs, snapshots, metrics, and alerts.

---

### Servers Table

```sql
CREATE TABLE servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    status TEXT DEFAULT 'unknown',
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### Container Snapshots Table

```sql
CREATE TABLE container_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    container_id TEXT,
    container_name TEXT,
    image TEXT,
    status TEXT,
    health TEXT,
    cpu_percent REAL,
    memory_mb REAL,
    memory_percent REAL,
    restart_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES servers(id)
);
```

---

### System Snapshots Table

```sql
CREATE TABLE system_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    cpu_percent REAL,
    memory_percent REAL,
    disk_percent REAL,
    uptime_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES servers(id)
);
```

---

### Alerts Table

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT,
    resolved BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY(server_id) REFERENCES servers(id)
);
```

---

### Health Checks Table

```sql
CREATE TABLE health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    target TEXT NOT NULL,
    expected_status INTEGER,
    timeout_seconds INTEGER DEFAULT 5,
    enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES servers(id)
);
```

---

### Health Check Results Table

```sql
CREATE TABLE health_check_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    health_check_id INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(health_check_id) REFERENCES health_checks(id)
);
```

---

## Installation Guide

This guide assumes a Linux VPS with Docker installed.

---

### Requirements

On the VPS:

* Linux server
* Docker
* Docker Compose
* Open firewall access only through private network or secure HTTPS

On the local PC:

* Python 3.11+
* Node.js 20+
* npm
* Git

Optional but recommended:

* Tailscale
* WireGuard
* Reverse proxy with HTTPS

---

## Docker Compose Setup

Example `docker-compose.yml` for the VPS Agent:

```yaml
services:
  sentinel-agent:
    build: ./agent
    container_name: sentinel-agent
    restart: unless-stopped
    ports:
      - "127.0.0.1:8443:8443"
    environment:
      - SENTINEL_API_KEY=${SENTINEL_API_KEY}
      - SERVER_NAME=${SERVER_NAME}
      - LOG_LEVEL=info
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /:/host:ro
```

This binds the agent only to `127.0.0.1` on the VPS.

If you want to reach it remotely, use a reverse proxy, SSH tunnel, Tailscale, or WireGuard.

---

## Environment Variables

Example `.env`:

```env
SENTINEL_API_KEY=change_this_to_a_long_random_secret
SERVER_NAME=william-vps-01
LOG_LEVEL=info
AGENT_PORT=8443
```

Recommended API key generation:

```bash
openssl rand -hex 32
```

---

## Running the Agent

Clone the repository:

```bash
git clone https://github.com/yourusername/sentinel.git
cd sentinel
```

Create environment file:

```bash
cp .env.example .env
nano .env
```

Start the agent:

```bash
docker compose up -d --build sentinel-agent
```

Check logs:

```bash
docker logs -f sentinel-agent
```

Test locally from the VPS:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://127.0.0.1:8443/api/ping
```

Expected response:

```json
{
  "status": "ok",
  "agent": "sentinel-agent",
  "version": "0.1.0",
  "server_name": "william-vps-01"
}
```

---

## Running the Local Dashboard

Start backend:

```bash
cd dashboard-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Add your VPS Agent URL and API key in the dashboard settings.

Example server config:

```text
Name: william-vps-01
URL: http://100.x.x.x:8443
API Key: your-long-secret-key
```

---

## Using Tailscale or WireGuard

The safest setup is to avoid exposing the agent publicly.

Recommended network design:

```text
Your PC <-- Tailscale/WireGuard --> VPS
```

Then the agent can listen on a private IP.

Example:

```text
http://100.64.12.34:8443
```

Benefits:

* No public API exposure
* Less firewall complexity
* Encrypted connection
* Easier access control
* Works well for personal infrastructure

---

## Alerting System

Alerts can be generated either by the agent or by the local dashboard.

Recommended MVP design:

* Agent returns raw status
* Local dashboard evaluates alert rules
* Dashboard stores alert history

Example alert rules:

```text
IF container.status != "running"
THEN critical alert
```

```text
IF disk.percent > 85
THEN warning alert
```

```text
IF disk.percent > 95
THEN critical alert
```

```text
IF container.restart_count increased by more than 3 in 10 minutes
THEN warning alert
```

```text
IF health_check.status_code >= 500
THEN critical alert
```

---

### Alert Severity Levels

Suggested severity levels:

```text
info
warning
critical
```

Example usage:

* `info`: New container detected
* `warning`: Disk usage above 85%
* `critical`: Container stopped unexpectedly

---

## Logging System

The project should keep two types of logs:

### Agent Logs

The agent should log:

* Startup
* Shutdown
* Authentication failures
* API requests
* Docker connection failures
* Internal errors

Example:

```text
[INFO] Agent started on port 8443
[INFO] Docker client connected
[WARN] Invalid API key from 192.168.1.50
[ERROR] Failed to read logs for container muf-site
```

### Dashboard Logs

The dashboard should log:

* Server added
* Server unreachable
* Polling failures
* Alert generated
* Alert resolved
* Database errors

---

## Metrics Collection

Metrics should be collected at intervals.

Suggested intervals:

```text
System metrics: every 10 seconds
Container status: every 10 seconds
Container stats: every 15 seconds
Health checks: every 30 seconds
SSL checks: every 6 hours
Disk usage: every 30 seconds
```

For the first version, keep it simple:

```text
Poll everything every 15 seconds while dashboard backend is running.
```

---

## MVP Scope

The first working version should include only what is needed to make the system useful.

### Agent MVP

* API key authentication
* `/api/ping`
* `/api/system`
* `/api/docker`
* `/api/docker/containers`
* `/api/docker/containers/{name}`
* `/api/docker/containers/{name}/logs`
* `/api/docker/containers/{name}/stats`

### Dashboard MVP

* Add server
* Store server URL and API key
* Show server online/offline
* Show CPU/RAM/disk
* Show all containers
* Show container status
* Show container logs
* Show simple alerts

---

## Roadmap

### Version 0.1 — Basic Read-Only Agent

* FastAPI agent
* Docker socket read access
* API key auth
* List containers
* Show system metrics
* Show logs

---

### Version 0.2 — Local Dashboard

* React dashboard
* Add monitored server
* Container table
* Server cards
* Log viewer
* Basic status badges

---

### Version 0.3 — Historical Metrics

* SQLite database
* Store system snapshots
* Store container snapshots
* CPU/RAM/disk charts
* Container restart timeline

---

### Version 0.4 — Alerts

* Alert rules
* Alert history
* Severity levels
* Resolved/unresolved status
* Dashboard alert page

---

### Version 0.5 — Health Checks

* HTTP checks
* Port checks
* SSL expiry checks
* Response time checks
* Health check result history

---

### Version 0.6 — Multi-Server Support

* Multiple VPS nodes
* Server grouping
* Tags
* Server notes
* Environment labels such as production, test, homelab

---

### Version 0.7 — Notifications

* Discord webhook alerts
* Email alerts
* Telegram alerts
* Push notifications

---

### Version 0.8 — Safe Remote Actions

Optional and disabled by default:

* Restart container
* Start container
* Stop container
* Pull image
* Run backup command

These actions should require an additional admin token or manual confirmation.

---

### Version 1.0 — Stable Release

* Secure deployment guide
* Full API documentation
* Better UI
* User accounts for dashboard
* Encrypted credential storage
* Agent update checker
* Export reports
* Backup dashboard data

---

## Security Notes

### Docker Socket Warning

Mounting the Docker socket gives the agent access to Docker Engine information.

Even with this mount:

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro
```

it should still be treated as sensitive.

Why?

* Container logs may contain secrets
* Environment variables may contain credentials
* Container metadata may reveal internal architecture
* Docker access can expose private service names and networks

The API should never return full environment variables by default.

---

### Do Not Expose Without Protection

Avoid exposing this directly to the public internet:

```text
https://your-vps.com:8443
```

A better setup:

```text
http://tailscale-private-ip:8443
```

or:

```text
ssh -L 8443:127.0.0.1:8443 user@your-vps
```

Then access:

```text
http://localhost:8443
```

---

### API Key Rules

Use a long random API key.

Good:

```text
64+ random hex characters
```

Bad:

```text
password123
admin
secret
william
```

Generate one:

```bash
openssl rand -hex 32
```

---

### Secrets Handling

The dashboard should hide or redact secrets.

Examples of sensitive keys to redact:

```text
PASSWORD
SECRET
TOKEN
API_KEY
PRIVATE_KEY
DATABASE_URL
ACCESS_KEY
AUTH
SESSION
COOKIE
```

Example redaction:

```json
{
  "DATABASE_URL": "[REDACTED]",
  "API_KEY": "[REDACTED]"
}
```

---

## Development Notes

### Suggested Python Packages for Agent

```text
fastapi
uvicorn
pydantic
python-dotenv
docker
psutil
httpx
```

Install:

```bash
pip install fastapi uvicorn pydantic python-dotenv docker psutil httpx
```

---

### Suggested Python Packages for Dashboard Backend

```text
fastapi
uvicorn
sqlalchemy
sqlmodel
pydantic
python-dotenv
httpx
cryptography
apscheduler
```

---

### Suggested Frontend Packages

```text
react
vite
typescript
tailwindcss
recharts
lucide-react
axios
```

---

## Example Agent Pseudocode

```python
from fastapi import FastAPI, Header, HTTPException
import docker
import psutil
import os

app = FastAPI()
client = docker.from_env()
API_KEY = os.getenv("SENTINEL_API_KEY")


def require_auth(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")

    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.get("/api/ping")
def ping(authorization: str = Header(None)):
    require_auth(authorization)
    return {"status": "ok"}


@app.get("/api/system")
def system(authorization: str = Header(None)):
    require_auth(authorization)
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }


@app.get("/api/docker/containers")
def containers(authorization: str = Header(None)):
    require_auth(authorization)
    result = []

    for c in client.containers.list(all=True):
        result.append({
            "id": c.id,
            "short_id": c.short_id,
            "name": c.name,
            "image": c.image.tags,
            "status": c.status,
        })

    return result
```

This is not the final code, but it shows the basic idea.

---

## UI Ideas

### Status Badges

Use clear visual labels:

```text
running      green
healthy      green
unhealthy    red
exited       gray
warning      yellow
critical     red
unknown      gray
```

---

### Dashboard Cards

Example cards:

```text
CPU Usage
RAM Usage
Disk Usage
Running Containers
Unhealthy Containers
Active Alerts
SSL Expiry
Latest Error
```

---

### Container Table Columns

Recommended columns:

```text
Name
Status
Health
Image
CPU
RAM
Ports
Restart Count
Uptime
Actions
```

---

## Future Ideas

### Remote Management Mode

Add optional remote actions:

* Restart container
* Start container
* Stop container
* Pull latest image
* Recreate service
* Run backup script

These should be disabled by default and protected by a separate admin token.

---

### Docker Compose Awareness

Detect Docker Compose projects and group containers by stack.

Example:

```text
Stack: muf-site
├── web
├── nginx
└── redis
```

Useful fields:

* Compose project name
* Compose service name
* Compose working directory
* Compose config files

---

### Nginx Integration

Add checks for:

* Nginx running
* Nginx config valid
* Sites enabled
* Reverse proxy targets
* HTTP status per domain
* SSL certificate expiry

---

### Backup System

Add a backup page:

```text
Backups
├── Database backups
├── Docker volume backups
├── Config backups
└── Manual backup button
```

Example backup targets:

* `/opt/apps`
* Docker volumes
* SQLite databases
* Nginx configs
* `.env` templates without secrets

---

### Public Status Page

Optional public page with limited data:

```text
muf-site: Operational
api: Operational
dashboard: Operational
Last incident: None
```

This should not expose internal Docker details.

---

### Discord Alerts

Example Discord alert:

```text
[Sentinel] Critical Alert
Server: william-vps-01
Container: muf-site
Problem: Container stopped unexpectedly
Time: 2026-04-30 18:42
```

---

### AI Log Summaries

Optional local AI integration:

* Summarize recent logs
* Explain errors
* Suggest fixes
* Detect repeated failure patterns

Example:

```text
The app appears to be failing because it cannot write to /app/activity.log. This is likely a file permission issue caused by the container running as a non-root user while the mounted file is owned by root.
```

---

## Design Goals

Sentinel should be:

* Simple to deploy
* Secure by default
* Read-only by default
* Useful for real VPS maintenance
* Easy to expand
* Clean and modern in the UI
* Lightweight enough for small servers
* Built for personal infrastructure

---

## Non-Goals

The project should not try to be a full enterprise monitoring platform.

Not intended for MVP:

* Kubernetes support
* Multi-user enterprise RBAC
* Full SIEM replacement
* Complex distributed tracing
* Heavy log indexing
* Public SaaS hosting
* Automatic destructive remediation

---

## Suggested First Milestone

The first useful milestone:

```text
Open local dashboard and see:

- VPS online/offline
- CPU/RAM/disk usage
- All Docker containers
- Running/stopped status
- Container logs
- Basic warning if disk is over 85%
```

Once this works, the project is already useful.

---

## Example Final Vision

Long-term, Sentinel could become a personal infrastructure control center.

```text
Sentinel
├── william-vps-01
│   ├── Docker containers
│   ├── Logs
│   ├── Metrics
│   ├── Health checks
│   └── Alerts
├── home-server-01
│   ├── Game servers
│   ├── Backups
│   └── Media services
└── raspberrypi-01
    ├── Pi-hole
    ├── Network monitor
    └── Local sensors
```

Instead of logging into each server manually, you get one clean local dashboard for everything.

---

## License

This project can be released under the MIT License.

Example:

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
```

---

## Final Summary

Sentinel is a practical self-hosted monitoring dashboard for Docker-based VPS setups.

The MVP should focus on:

* A secure read-only VPS Agent
* A local dashboard
* Docker container status
* System metrics
* Logs
* Basic alerts

After that, the project can grow into a full personal infrastructure dashboard with multi-server support, historical metrics, notifications, backups, and safe remote management.
