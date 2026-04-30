import { FileText, RotateCw } from "lucide-react";
import StatusBadge from "./StatusBadge";

type Container = {
  id: string;
  name: string;
  image: string;
  status: string;
  health?: string;
  cpu_percent?: number | null;
  memory_mb?: number | null;
  restart_count?: number;
  server_id?: number;
  server_name?: string;
};

type Props = {
  containers: Container[];
  onLogs?: (container: Container) => void;
  onRestart?: (container: Container) => void;
};

export default function ContainerTable({ containers, onLogs, onRestart }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-line bg-panel shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-normal text-slate-500">
            <tr>
              <th className="px-3 py-3">Name</th>
              <th className="px-3 py-3">Server</th>
              <th className="px-3 py-3">Status</th>
              <th className="px-3 py-3">Health</th>
              <th className="px-3 py-3">Image</th>
              <th className="px-3 py-3">CPU</th>
              <th className="px-3 py-3">RAM</th>
              <th className="px-3 py-3">Restarts</th>
              <th className="px-3 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {containers.map((container) => (
              <tr key={`${container.server_name || ""}-${container.id}`} className="hover:bg-slate-50">
                <td className="px-3 py-3 font-medium text-ink">{container.name}</td>
                <td className="px-3 py-3 text-slate-500">{container.server_name || "--"}</td>
                <td className="px-3 py-3"><StatusBadge value={container.status} /></td>
                <td className="px-3 py-3"><StatusBadge value={container.health || "none"} /></td>
                <td className="max-w-64 truncate px-3 py-3 text-slate-600">{container.image}</td>
                <td className="px-3 py-3 text-slate-600">{container.cpu_percent ?? "--"}%</td>
                <td className="px-3 py-3 text-slate-600">{container.memory_mb ?? "--"} MB</td>
                <td className="px-3 py-3 text-slate-600">{container.restart_count ?? 0}</td>
                <td className="px-3 py-3">
                  <div className="flex justify-end gap-2">
                    {onLogs && (
                      <button className="focus-ring rounded border border-line p-2 text-slate-600 hover:bg-slate-100" title="View logs" onClick={() => onLogs(container)}>
                        <FileText size={16} />
                      </button>
                    )}
                    {onRestart && (
                      <button className="focus-ring rounded border border-line p-2 text-slate-600 hover:bg-slate-100" title="Restart container" onClick={() => onRestart(container)}>
                        <RotateCw size={16} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {containers.length === 0 && (
              <tr>
                <td className="px-3 py-8 text-center text-slate-500" colSpan={9}>No container snapshots yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
