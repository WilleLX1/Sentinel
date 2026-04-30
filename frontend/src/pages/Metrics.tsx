import { useEffect, useState } from "react";
import { api } from "../api/client";
import CpuChart from "../charts/CpuChart";
import DiskChart from "../charts/DiskChart";
import MemoryChart from "../charts/MemoryChart";

export default function Metrics() {
  const [servers, setServers] = useState<any[]>([]);
  const [serverId, setServerId] = useState<number | "">("");
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    api.get<any[]>("/api/servers").then((items) => {
      setServers(items);
      if (items[0]) setServerId(items[0].id);
    });
  }, []);

  useEffect(() => {
    if (serverId) api.get<any[]>(`/api/servers/${serverId}/metrics/system?hours=24`).then(setMetrics);
  }, [serverId]);

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-line bg-panel p-4 shadow-sm">
        <select className="focus-ring rounded border border-line px-3 py-2" value={serverId} onChange={(e) => setServerId(Number(e.target.value))}>
          <option value="">Server</option>
          {servers.map((server) => <option key={server.id} value={server.id}>{server.name}</option>)}
        </select>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">CPU</h3><CpuChart data={metrics} /></div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">RAM</h3><MemoryChart data={metrics} /></div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">Disk</h3><DiskChart data={metrics} /></div>
      </div>
    </div>
  );
}

