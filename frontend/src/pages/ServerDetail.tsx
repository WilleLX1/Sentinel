import { Activity, AlertTriangle, Cpu, HardDrive, MemoryStick } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import CpuChart from "../charts/CpuChart";
import DiskChart from "../charts/DiskChart";
import MemoryChart from "../charts/MemoryChart";
import ContainerTable from "../components/ContainerTable";
import MetricCard from "../components/MetricCard";
import StatusBadge from "../components/StatusBadge";

export default function ServerDetail({ serverId, navigate }: { serverId: number; navigate: (route: string) => void }) {
  const [server, setServer] = useState<any>(null);
  const [containers, setContainers] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any[]>([]);

  async function load() {
    setServer(await api.get(`/api/servers/${serverId}`));
    setContainers(await api.get(`/api/servers/${serverId}/containers`));
    setMetrics(await api.get(`/api/servers/${serverId}/metrics/system?hours=24`));
  }

  useEffect(() => {
    load();
  }, [serverId]);

  const latest = metrics[metrics.length - 1];

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-line bg-panel p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-ink">{server?.name || "Server"}</h2>
            <p className="mt-1 text-sm text-slate-500">{server?.url}</p>
          </div>
          <StatusBadge value={server?.status} />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="CPU" value={`${latest?.cpu_percent ?? "--"}%`} icon={Cpu} />
        <MetricCard title="RAM" value={`${latest?.memory_percent ?? "--"}%`} icon={MemoryStick} />
        <MetricCard title="Disk" value={`${latest?.disk_percent ?? "--"}%`} icon={HardDrive} />
        <MetricCard title="Containers" value={containers.length} detail={`${containers.filter((c) => c.status === "running").length} running`} icon={Activity} />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">CPU</h3><CpuChart data={metrics} /></div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">RAM</h3><MemoryChart data={metrics} /></div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-sm"><h3 className="mb-3 font-semibold text-ink">Disk</h3><DiskChart data={metrics} /></div>
      </div>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <AlertTriangle size={18} />
          <h3 className="text-lg font-semibold text-ink">Containers</h3>
        </div>
        <ContainerTable containers={containers} onLogs={(container) => navigate(`logs:${serverId}:${container.id}`)} />
      </section>
    </div>
  );
}

