from __future__ import annotations

import os
import platform
import socket
import time

import psutil

from .config import get_settings


def _bytes_to_mb(value: float) -> float:
    return round(value / 1024 / 1024, 2)


def _bytes_to_gb(value: float) -> float:
    return round(value / 1024 / 1024 / 1024, 2)


def _ip_addresses() -> list[str]:
    addresses: list[str] = []
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family in (socket.AF_INET, socket.AF_INET6) and not addr.address.startswith("127."):
                addresses.append(addr.address)
    return sorted(set(addresses))


def system_overview() -> dict:
    settings = get_settings()
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk_path = settings.disk_path if os.path.exists(settings.disk_path) else "/"
    disk = psutil.disk_usage(disk_path)
    net = psutil.net_io_counters()
    boot_time = psutil.boot_time()

    try:
        load_average = os.getloadavg()
    except (AttributeError, OSError):
        load_average = (0.0, 0.0, 0.0)

    return {
        "hostname": socket.gethostname(),
        "server_name": settings.server_name,
        "os": platform.platform(),
        "kernel": platform.release(),
        "python_version": platform.python_version(),
        "uptime_seconds": int(time.time() - boot_time),
        "boot_time": int(boot_time),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "load_average": list(load_average),
        "memory": {
            "total_mb": _bytes_to_mb(memory.total),
            "used_mb": _bytes_to_mb(memory.used),
            "available_mb": _bytes_to_mb(memory.available),
            "percent": memory.percent,
        },
        "swap": {
            "total_mb": _bytes_to_mb(swap.total),
            "used_mb": _bytes_to_mb(swap.used),
            "percent": swap.percent,
        },
        "disk": {
            "path": disk_path,
            "total_gb": _bytes_to_gb(disk.total),
            "used_gb": _bytes_to_gb(disk.used),
            "free_gb": _bytes_to_gb(disk.free),
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent_mb": _bytes_to_mb(net.bytes_sent),
            "bytes_recv_mb": _bytes_to_mb(net.bytes_recv),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
        "processes": {
            "running": len(psutil.pids()),
        },
        "ip_addresses": _ip_addresses(),
    }

