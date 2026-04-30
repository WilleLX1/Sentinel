from __future__ import annotations

from functools import lru_cache
from typing import Any

import docker
from docker.errors import DockerException, NotFound

from .security import redact_env


class DockerUnavailable(RuntimeError):
    pass


def _mb(value: float | int | None) -> float:
    return round((value or 0) / 1024 / 1024, 2)


def _image_name(container: Any) -> str:
    tags = getattr(container.image, "tags", None) or []
    if tags:
        return tags[0]
    return container.attrs.get("Config", {}).get("Image") or getattr(container.image, "short_id", "unknown")


def _health(attrs: dict) -> str:
    return attrs.get("State", {}).get("Health", {}).get("Status") or "none"


def _ports(attrs: dict) -> list[dict]:
    result: list[dict] = []
    ports = attrs.get("NetworkSettings", {}).get("Ports") or {}
    for raw_port, bindings in ports.items():
        container_port, _, protocol = raw_port.partition("/")
        if not bindings:
            result.append(
                {
                    "container_port": int(container_port) if container_port.isdigit() else container_port,
                    "host_ip": None,
                    "host_port": None,
                    "protocol": protocol or "tcp",
                }
            )
            continue
        for binding in bindings:
            host_port = binding.get("HostPort")
            result.append(
                {
                    "container_port": int(container_port) if container_port.isdigit() else container_port,
                    "host_ip": binding.get("HostIp"),
                    "host_port": int(host_port) if host_port and host_port.isdigit() else host_port,
                    "protocol": protocol or "tcp",
                }
            )
    return result


def _networks(attrs: dict) -> list[str]:
    return sorted((attrs.get("NetworkSettings", {}).get("Networks") or {}).keys())


def _volumes(attrs: dict) -> list[dict]:
    volumes: list[dict] = []
    for mount in attrs.get("Mounts", []) or []:
        volumes.append(
            {
                "name": mount.get("Name"),
                "source": mount.get("Source"),
                "destination": mount.get("Destination"),
                "driver": mount.get("Driver"),
                "mode": mount.get("Mode"),
                "rw": mount.get("RW"),
                "type": mount.get("Type"),
            }
        )
    return volumes


@lru_cache
def docker_service() -> "DockerService":
    return DockerService()


class DockerService:
    def __init__(self) -> None:
        self._client = None

    def client(self):
        if self._client is None:
            try:
                self._client = docker.from_env()
                self._client.ping()
            except DockerException as exc:
                raise DockerUnavailable(str(exc)) from exc
        return self._client

    def overview(self) -> dict:
        try:
            client = self.client()
            containers = client.containers.list(all=True)
            images = client.images.list()
            volumes = client.volumes.list()
            networks = client.networks.list()
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc

        return {
            "docker_available": True,
            "containers_total": len(containers),
            "containers_running": sum(1 for c in containers if c.status == "running"),
            "containers_stopped": sum(1 for c in containers if c.status != "running"),
            "containers_unhealthy": sum(1 for c in containers if _health(c.attrs) == "unhealthy"),
            "images_total": len(images),
            "volumes_total": len(volumes),
            "networks_total": len(networks),
        }

    def container_summary(self, container: Any) -> dict:
        attrs = container.attrs
        state = attrs.get("State", {})
        return {
            "id": container.id,
            "short_id": container.short_id,
            "name": container.name,
            "image": _image_name(container),
            "status": container.status,
            "health": _health(attrs),
            "created": attrs.get("Created"),
            "started_at": state.get("StartedAt"),
            "finished_at": state.get("FinishedAt"),
            "restart_count": attrs.get("RestartCount", 0),
            "ports": _ports(attrs),
            "networks": _networks(attrs),
            "compose_project": attrs.get("Config", {}).get("Labels", {}).get("com.docker.compose.project"),
            "compose_service": attrs.get("Config", {}).get("Labels", {}).get("com.docker.compose.service"),
        }

    def list_containers(self) -> list[dict]:
        try:
            return [self.container_summary(c) for c in self.client().containers.list(all=True)]
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc

    def get_container(self, id_or_name: str) -> dict:
        try:
            container = self.client().containers.get(id_or_name)
            container.reload()
        except NotFound as exc:
            raise
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc

        attrs = container.attrs
        config = attrs.get("Config", {})
        state = attrs.get("State", {})
        result = self.container_summary(container)
        result.update(
            {
                "labels": config.get("Labels") or {},
                "env": redact_env(config.get("Env")),
                "command": config.get("Cmd"),
                "entrypoint": config.get("Entrypoint"),
                "last_error": state.get("Error") or None,
                "exit_code": state.get("ExitCode"),
                "networks": _networks(attrs),
                "volumes": _volumes(attrs),
            }
        )
        return result

    def logs(self, id_or_name: str, lines: int = 100, since: str | None = None, filter_text: str | None = None) -> dict:
        try:
            container = self.client().containers.get(id_or_name)
            kwargs: dict[str, Any] = {"tail": max(1, min(lines, 2000)), "timestamps": True}
            if since:
                kwargs["since"] = since
            raw = container.logs(**kwargs).decode("utf-8", errors="replace")
        except NotFound:
            raise
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc

        log_lines = raw.splitlines()
        if filter_text:
            needle = filter_text.lower()
            log_lines = [line for line in log_lines if needle in line.lower()]
        return {"container": container.name, "lines": log_lines[-lines:]}

    def stats(self, id_or_name: str) -> dict:
        try:
            container = self.client().containers.get(id_or_name)
            stats = container.stats(stream=False)
        except NotFound:
            raise
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc

        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})
        cpu_delta = (
            cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
        )
        system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
        online_cpus = cpu_stats.get("online_cpus") or len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", []) or []) or 1
        cpu_percent = (cpu_delta / system_delta * online_cpus * 100.0) if system_delta > 0 else 0.0

        memory_stats = stats.get("memory_stats", {})
        memory_usage = memory_stats.get("usage", 0) - memory_stats.get("stats", {}).get("cache", 0)
        memory_limit = memory_stats.get("limit", 0)
        memory_percent = (memory_usage / memory_limit * 100.0) if memory_limit else 0.0

        networks = stats.get("networks") or {}
        rx = sum(interface.get("rx_bytes", 0) for interface in networks.values())
        tx = sum(interface.get("tx_bytes", 0) for interface in networks.values())

        return {
            "container": container.name,
            "cpu_percent": round(cpu_percent, 2),
            "memory_usage_mb": _mb(memory_usage),
            "memory_limit_mb": _mb(memory_limit),
            "memory_percent": round(memory_percent, 2),
            "network_rx_mb": _mb(rx),
            "network_tx_mb": _mb(tx),
        }

    def images(self) -> list[dict]:
        try:
            images = self.client().images.list()
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc
        return [
            {
                "id": image.id,
                "short_id": image.short_id,
                "tags": image.tags,
                "size_mb": _mb(image.attrs.get("Size")),
                "created": image.attrs.get("Created"),
            }
            for image in images
        ]

    def networks(self) -> list[dict]:
        try:
            networks = self.client().networks.list()
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc
        result = []
        for network in networks:
            attrs = network.attrs
            containers = attrs.get("Containers") or {}
            result.append(
                {
                    "id": network.id,
                    "short_id": network.short_id,
                    "name": network.name,
                    "driver": attrs.get("Driver"),
                    "scope": attrs.get("Scope"),
                    "containers": [value.get("Name") for value in containers.values() if value.get("Name")],
                }
            )
        return result

    def volumes(self) -> list[dict]:
        try:
            volumes = self.client().volumes.list()
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc
        return [
            {
                "name": volume.name,
                "driver": volume.attrs.get("Driver"),
                "mountpoint": volume.attrs.get("Mountpoint"),
                "labels": volume.attrs.get("Labels") or {},
                "created_at": volume.attrs.get("CreatedAt"),
            }
            for volume in volumes
        ]

    def container_action(self, id_or_name: str, action: str) -> dict:
        try:
            container = self.client().containers.get(id_or_name)
            if action == "restart":
                container.restart()
            elif action == "start":
                container.start()
            elif action == "stop":
                container.stop()
            else:
                raise ValueError(f"Unsupported action: {action}")
        except NotFound:
            raise
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc
        return {"container": container.name, "action": action, "status": "accepted"}

    def pull_image(self, image: str) -> dict:
        try:
            pulled = self.client().images.pull(image)
        except DockerException as exc:
            self._client = None
            raise DockerUnavailable(str(exc)) from exc
        return {"image": image, "id": pulled.id, "tags": pulled.tags, "status": "pulled"}

