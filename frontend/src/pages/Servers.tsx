import { CheckCircle, Plus, RefreshCw, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

type Server = {
  id: number;
  name: string;
  url: string;
  status: string;
  environment: string;
  notes: string;
  last_seen?: string;
  action_key_configured: boolean;
};

const empty = { name: "", url: "", api_key: "", action_key: "", environment: "production", notes: "" };

export default function Servers({ navigate }: { navigate: (route: string) => void }) {
  const [servers, setServers] = useState<Server[]>([]);
  const [form, setForm] = useState(empty);
  const [message, setMessage] = useState("");

  async function load() {
    setServers(await api.get<Server[]>("/api/servers"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post("/api/servers", form);
    setForm(empty);
    await load();
  }

  async function test(id: number) {
    const result = await api.post<any>(`/api/servers/${id}/test`);
    setMessage(`${result.status}: ${result.response?.server_name || "agent"}`);
  }

  async function poll(id: number) {
    const result = await api.post<any>(`/api/servers/${id}/poll`);
    setMessage(`${result.status}: ${result.containers ?? 0} containers`);
    await load();
  }

  async function remove(id: number) {
    if (!window.confirm("Delete this server and stop polling it?")) return;
    await api.del(`/api/servers/${id}`);
    await load();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={submit}>
        <h2 className="text-lg font-semibold text-ink">Add Server</h2>
        <div className="mt-4 space-y-3">
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Agent URL" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="API key" value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Action key" value={form.action_key} onChange={(e) => setForm({ ...form, action_key: e.target.value })} />
          <select className="focus-ring w-full rounded border border-line px-3 py-2" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
            <option value="production">production</option>
            <option value="test">test</option>
            <option value="homelab">homelab</option>
          </select>
          <textarea className="focus-ring min-h-24 w-full rounded border border-line px-3 py-2" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
            <Plus size={16} /> Add server
          </button>
        </div>
      </form>

      <div className="space-y-3">
        {message && <div className="rounded border border-line bg-panel px-3 py-2 text-sm text-slate-600">{message}</div>}
        {servers.map((server) => (
          <div key={server.id} className="rounded-lg border border-line bg-panel p-4 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <button className="text-left" onClick={() => navigate(`server:${server.id}`)}>
                <h3 className="font-semibold text-ink">{server.name}</h3>
                <p className="mt-1 max-w-xl truncate text-sm text-slate-500">{server.url}</p>
              </button>
              <StatusBadge value={server.status} />
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={() => test(server.id)}>
                <CheckCircle size={16} /> Test
              </button>
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={() => poll(server.id)}>
                <RefreshCw size={16} /> Poll
              </button>
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-red-200 px-3 py-2 text-sm text-red-700 hover:bg-red-50" onClick={() => remove(server.id)}>
                <Trash2 size={16} /> Delete
              </button>
            </div>
          </div>
        ))}
        {servers.length === 0 && <div className="rounded-lg border border-line bg-panel p-6 text-center text-slate-500">No servers configured.</div>}
      </div>
    </div>
  );
}

