# Sentinel API

All agent endpoints require `Authorization: Bearer <SENTINEL_API_KEY>`.

Core agent endpoints:

- `GET /api/ping`
- `GET /api/system`
- `GET /api/docker`
- `GET /api/docker/containers`
- `GET /api/docker/containers/{id_or_name}`
- `GET /api/docker/containers/{id_or_name}/logs?lines=100&since=&filter=`
- `GET /api/docker/containers/{id_or_name}/stats`
- `GET /api/docker/images`
- `GET /api/docker/networks`
- `GET /api/docker/volumes`
- `GET /api/health/http?url=&expected_status=200&timeout=5`
- `GET /api/health/tcp?host=&port=&timeout=5`
- `GET /api/health/ssl?host=&port=443&timeout=5`

Action endpoints are disabled unless `SENTINEL_ACTIONS_ENABLED=true`. They require the normal bearer key plus `X-Sentinel-Action-Key`.

Dashboard endpoints are protected by an HTTP-only session cookie after `POST /api/auth/login`.

