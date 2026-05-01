import { useEffect, useState } from "react";
import { api } from "../api/client";
import ContainerTable from "../components/ContainerTable";

export default function Containers({ navigate }: { navigate: (route: string) => void }) {
  const [containers, setContainers] = useState<any[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    setContainers(await api.get("/api/containers"));
  }

  async function pruneStale() {
    const result = await api.post<{ removed: number }>("/api/containers/prune-stale");
    setMessage(`Removed ${result.removed} stale container snapshots`);
    await load();
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Containers</h2>
        <div className="flex gap-2">
          <button className="focus-ring rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={pruneStale}>Clean stale snapshots</button>
          <button className="focus-ring rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={load}>Refresh</button>
        </div>
      </div>
      {message && <div className="rounded border border-line bg-panel px-3 py-2 text-sm text-slate-600">{message}</div>}
      <ContainerTable
        containers={containers}
        onLogs={(container) => navigate(`logs:${container.server_id}:${container.id}`)}
        onRestart={(container) => navigate(`actions:${container.server_id}:${container.id}`)}
      />
    </div>
  );
}
