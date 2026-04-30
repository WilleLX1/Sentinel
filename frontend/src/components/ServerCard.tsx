import { Activity, AlertTriangle, Cpu, HardDrive, MemoryStick } from "lucide-react";
import StatusBadge from "./StatusBadge";

type Server = {
  id: number;
  name: string;
  url: string;
  status: string;
  environment?: string;
  cpu_percent?: number | null;
  memory_percent?: number | null;
  disk_percent?: number | null;
  running_containers?: number;
  containers_total?: number;
  active_alerts?: number;
};

export default function ServerCard({ server, onOpen }: { server: Server; onOpen: (id: number) => void }) {
  return (
    <button
      className="focus-ring w-full rounded-lg border border-line bg-panel p-4 text-left shadow-sm transition hover:border-slate-400"
      onClick={() => onOpen(server.id)}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-ink">{server.name}</h3>
          <p className="mt-1 max-w-full truncate text-sm text-slate-500">{server.url}</p>
        </div>
        <StatusBadge value={server.status} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2 text-sm text-slate-600 md:grid-cols-4">
        <span className="flex items-center gap-2"><Cpu size={15} />{server.cpu_percent ?? "--"}%</span>
        <span className="flex items-center gap-2"><MemoryStick size={15} />{server.memory_percent ?? "--"}%</span>
        <span className="flex items-center gap-2"><HardDrive size={15} />{server.disk_percent ?? "--"}%</span>
        <span className="flex items-center gap-2"><Activity size={15} />{server.running_containers ?? 0}/{server.containers_total ?? 0}</span>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-line pt-3 text-sm text-slate-500">
        <span>{server.environment || "production"}</span>
        <span className="flex items-center gap-1"><AlertTriangle size={15} />{server.active_alerts ?? 0} alerts</span>
      </div>
    </button>
  );
}

