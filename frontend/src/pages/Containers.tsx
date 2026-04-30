import { useEffect, useState } from "react";
import { api } from "../api/client";
import ContainerTable from "../components/ContainerTable";

export default function Containers({ navigate }: { navigate: (route: string) => void }) {
  const [containers, setContainers] = useState<any[]>([]);

  async function load() {
    setContainers(await api.get("/api/containers"));
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Containers</h2>
        <button className="focus-ring rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={load}>Refresh</button>
      </div>
      <ContainerTable
        containers={containers}
        onLogs={(container) => navigate(`logs:${container.server_id}:${container.id}`)}
        onRestart={(container) => navigate(`actions:${container.server_id}:${container.id}`)}
      />
    </div>
  );
}

