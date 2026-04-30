import { Search } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import LogViewer from "../components/LogViewer";

export default function Logs({ initialServerId, initialContainerId }: { initialServerId?: number; initialContainerId?: string }) {
  const [servers, setServers] = useState<any[]>([]);
  const [containers, setContainers] = useState<any[]>([]);
  const [serverId, setServerId] = useState<number | "">(initialServerId || "");
  const [containerId, setContainerId] = useState(initialContainerId || "");
  const [filter, setFilter] = useState("");
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    api.get<any[]>("/api/servers").then(setServers);
  }, []);

  useEffect(() => {
    if (serverId) {
      api.get<any[]>(`/api/servers/${serverId}/containers`).then((items) => {
        setContainers(items);
        if (!containerId && items[0]) setContainerId(items[0].id);
      });
    }
  }, [serverId]);

  useEffect(() => {
    if (initialServerId && initialContainerId) {
      fetchLogs(initialServerId, initialContainerId);
    }
  }, [initialServerId, initialContainerId]);

  async function fetchLogs(selectedServer = serverId, selectedContainer = containerId) {
    if (!selectedServer || !selectedContainer) return;
    const query = new URLSearchParams({ lines: "500" });
    if (filter) query.set("filter", filter);
    const result = await api.get<{ lines: string[] }>(`/api/servers/${selectedServer}/containers/${selectedContainer}/logs?${query.toString()}`);
    setLines(result.lines);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await fetchLogs();
  }

  return (
    <div className="space-y-4">
      <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={submit}>
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_auto]">
          <select className="focus-ring rounded border border-line px-3 py-2" value={serverId} onChange={(e) => setServerId(Number(e.target.value))}>
            <option value="">Server</option>
            {servers.map((server) => <option key={server.id} value={server.id}>{server.name}</option>)}
          </select>
          <select className="focus-ring rounded border border-line px-3 py-2" value={containerId} onChange={(e) => setContainerId(e.target.value)}>
            <option value="">Container</option>
            {containers.map((container) => <option key={container.id} value={container.id}>{container.name}</option>)}
          </select>
          <input className="focus-ring rounded border border-line px-3 py-2" placeholder="Filter" value={filter} onChange={(e) => setFilter(e.target.value)} />
          <button className="focus-ring inline-flex items-center justify-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
            <Search size={16} /> Fetch
          </button>
        </div>
      </form>
      <LogViewer lines={lines} />
    </div>
  );
}

