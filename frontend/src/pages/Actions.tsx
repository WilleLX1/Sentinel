import { Download, Play, Power, RefreshCw, Square } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

type Server = {
  id: number;
  name: string;
  status: string;
  action_key_configured: boolean;
};

type Container = {
  id: string;
  name: string;
  image: string;
  status: string;
  health?: string;
  server_id?: number;
  server_name?: string;
};

const actions = [
  { id: "restart", label: "Restart", icon: RefreshCw, tone: "border-line text-slate-700 hover:bg-slate-50" },
  { id: "start", label: "Start", icon: Play, tone: "border-emerald-200 text-emerald-700 hover:bg-emerald-50" },
  { id: "stop", label: "Stop", icon: Square, tone: "border-red-200 text-red-700 hover:bg-red-50" }
] as const;

export default function Actions({ initialServerId, initialContainerId }: { initialServerId?: number; initialContainerId?: string }) {
  const [servers, setServers] = useState<Server[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [serverId, setServerId] = useState<number | "">(initialServerId || "");
  const [containerId, setContainerId] = useState(initialContainerId || "");
  const [image, setImage] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadServers() {
    const items = await api.get<Server[]>("/api/servers");
    setServers(items);
    if (!serverId && items[0]) setServerId(items[0].id);
  }

  async function loadContainers(selectedServerId = serverId) {
    if (!selectedServerId) {
      setContainers([]);
      return;
    }
    const items = await api.get<Container[]>(`/api/servers/${selectedServerId}/containers`);
    setContainers(items);
    if (!containerId && items[0]) setContainerId(items[0].id);
  }

  useEffect(() => {
    loadServers();
  }, []);

  useEffect(() => {
    loadContainers();
  }, [serverId]);

  async function runContainerAction(action: "restart" | "start" | "stop") {
    if (!serverId || !containerId) return;
    const container = containers.find((item) => item.id === containerId);
    const label = container?.name || containerId;
    if (!window.confirm(`${action} container "${label}"?`)) return;

    setBusy(true);
    setMessage("");
    try {
      const result = await api.post<any>(`/api/actions/servers/${serverId}/containers/${containerId}/${action}`);
      setMessage(`${action} accepted for ${result.container || label}`);
      await api.post(`/api/servers/${serverId}/poll`);
      await loadContainers(serverId);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  async function pullImage(event: FormEvent) {
    event.preventDefault();
    if (!serverId || !image.trim()) return;
    if (!window.confirm(`Pull image "${image.trim()}" on selected server?`)) return;

    setBusy(true);
    setMessage("");
    try {
      await api.post(`/api/actions/servers/${serverId}/images/pull`, { image: image.trim() });
      setMessage(`Image pull accepted: ${image.trim()}`);
      setImage("");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Image pull failed");
    } finally {
      setBusy(false);
    }
  }

  const selectedServer = servers.find((server) => server.id === serverId);
  const selectedContainer = containers.find((container) => container.id === containerId);

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        Container actions require the server action key and `SENTINEL_ACTIONS_ENABLED=true` on the agent.
      </div>

      {message && <div className="rounded-lg border border-line bg-panel px-4 py-3 text-sm text-slate-700 shadow-sm">{message}</div>}

      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <section className="rounded-lg border border-line bg-panel p-4 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Power size={18} />
            <h2 className="text-lg font-semibold text-ink">Container Actions</h2>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <select
              className="focus-ring rounded border border-line px-3 py-2"
              value={serverId}
              onChange={(event) => {
                setServerId(Number(event.target.value));
                setContainerId("");
              }}
            >
              <option value="">Server</option>
              {servers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.name}
                </option>
              ))}
            </select>

            <select className="focus-ring rounded border border-line px-3 py-2" value={containerId} onChange={(event) => setContainerId(event.target.value)}>
              <option value="">Container</option>
              {containers.map((container) => (
                <option key={container.id} value={container.id}>
                  {container.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mt-4 rounded border border-line bg-slate-50 p-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-medium text-ink">{selectedContainer?.name || "No container selected"}</p>
                <p className="mt-1 max-w-2xl truncate text-sm text-slate-500">{selectedContainer?.image || selectedServer?.name || "Select a server and container"}</p>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge value={selectedContainer?.status || "unknown"} />
                <StatusBadge value={selectedContainer?.health || "none"} />
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {actions.map(({ id, label, icon: Icon, tone }) => (
              <button
                key={id}
                className={`focus-ring inline-flex items-center gap-2 rounded border px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50 ${tone}`}
                disabled={!serverId || !containerId || busy}
                onClick={() => runContainerAction(id)}
              >
                <Icon size={16} /> {label}
              </button>
            ))}
          </div>
        </section>

        <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={pullImage}>
          <div className="mb-4 flex items-center gap-2">
            <Download size={18} />
            <h2 className="text-lg font-semibold text-ink">Pull Image</h2>
          </div>
          <div className="space-y-3">
            <select className="focus-ring w-full rounded border border-line px-3 py-2" value={serverId} onChange={(event) => setServerId(Number(event.target.value))}>
              <option value="">Server</option>
              {servers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.name}
                </option>
              ))}
            </select>
            <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="nginx:latest" value={image} onChange={(event) => setImage(event.target.value)} />
            <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50" disabled={!serverId || !image.trim() || busy}>
              <Download size={16} /> Pull image
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

