# Sentinel Development

Prerequisites:

- Python 3.11+
- Node.js 20+
- Docker

Agent:

```bash
cd agent
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8443
```

Dashboard backend:

```bash
cd dashboard-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The default development dashboard credentials are `admin` / `sentinel-admin`. Change them in `.env` before using Sentinel for real infrastructure.

