Use this layout:

```text
Main PC
  dashboard-backend on 127.0.0.1:8000
  frontend on 127.0.0.1:5173

Debian VPS
  sentinel-agent on http://<tailscale-ip>:8443
  Docker socket mounted read-only
```

**1. Put both machines on Tailscale**
On Debian VPS:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

Install/sign in to Tailscale on your main PC too. Save the VPS Tailscale IP, usually `100.x.x.x`.

**2. Set up the agent on Debian VPS**
Install Docker if needed, then clone your repo:

```bash
sudo apt update
sudo apt install -y git

git clone https://github.com/WilleLX1/Sentinel.git
cd Sentinel
cp .env.example .env
nano .env
```

Generate an API key:

```bash
openssl rand -hex 32
```

Set at least:

```env
SENTINEL_API_KEY=use_a_long_random_secret_here
SERVER_NAME=my-vps
AGENT_PORT=8443
SENTINEL_ACTIONS_ENABLED=false
```

Because the current `docker-compose.yml` binds the agent to `127.0.0.1`, add a VPS override that exposes it only on the Tailscale IP:

```bash
cat > docker-compose.vps.yml <<'YAML'
services:
  sentinel-agent:
    ports:
      - "YOUR_TAILSCALE_IP:8443:8443"
YAML
```

Replace `YOUR_TAILSCALE_IP`, then start only the agent:

```bash
docker compose -f docker-compose.yml -f docker-compose.vps.yml up -d --build sentinel-agent
```

Test from your main PC:

```powershell
Invoke-RestMethod `
  -Uri http://YOUR_TAILSCALE_IP:8443/api/ping `
  -Headers @{ Authorization = "Bearer YOUR_SENTINEL_API_KEY" }
```

**3. Set up the dashboard on your main PC**
From `C:\projects\Python\Sentinel`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r dashboard-backend\requirements.txt

cd frontend
npm install
npm run build
cd ..
```

Create `dashboard-backend\.env`:

```env
DASHBOARD_SESSION_SECRET=change_this_to_a_long_random_secret
DASHBOARD_ADMIN_USERNAME=admin
DASHBOARD_ADMIN_PASSWORD=use_a_real_password
DASHBOARD_DATABASE_URL=sqlite:///./data/sentinel.db
```

Start backend and frontend in two terminals:

```powershell
cd C:\projects\Python\Sentinel\dashboard-backend
..\ .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd C:\projects\Python\Sentinel\frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Then add the VPS in the UI:

```text
Name: my-vps
URL: http://YOUR_TAILSCALE_IP:8443
API Key: YOUR_SENTINEL_API_KEY
```

Do not expose `8443` on the VPS public IP. Binding it to the Tailscale IP is the important safety step.

If you do any updates, keep in mind that you need to update the sentinel agent (in sentinel root):
```bash
docker compose up -d --build --force-recreate sentinel-agent
```

Sources: [Tailscale Linux install docs](https://tailscale.com/docs/install/linux), [Docker Debian install docs](https://docs.docker.com/engine/install/debian/).