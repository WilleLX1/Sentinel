import { CheckCircle, Pencil, Plus, RefreshCw, Save, Trash2, X } from "lucide-react";
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
  api_key_configured: boolean;
  action_key_configured: boolean;
};

const empty = { name: "", url: "", api_key: "", action_key: "", environment: "production", notes: "" };

export default function Servers({ navigate }: { navigate: (route: string) => void }) {
  const [servers, setServers] = useState<Server[]>([]);
  const [form, setForm] = useState(empty);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    setServers(await api.get<Server[]>("/api/servers"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (editingId) {
      const payload: Record<string, string> = {
        name: form.name,
        url: form.url,
        environment: form.environment,
        notes: form.notes
      };
      if (form.api_key.trim()) payload.api_key = form.api_key;
      if (form.action_key.trim()) payload.action_key = form.action_key;
      await api.put(`/api/servers/${editingId}`, payload);
      setMessage("Server updated");
    } else {
      await api.post("/api/servers", form);
      setMessage("Server added");
    }
    setForm(empty);
    setEditingId(null);
    await load();
  }

  function edit(server: Server) {
    setEditingId(server.id);
    setForm({
      name: server.name,
      url: server.url,
      api_key: "",
      action_key: "",
      environment: server.environment || "production",
      notes: server.notes || ""
    });
    setMessage("Leave API key fields blank to keep existing secrets");
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(empty);
    setMessage("");
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
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">{editingId ? "Edit Server" : "Add Server"}</h2>
          {editingId && (
            <button type="button" className="focus-ring rounded border border-line p-2 text-slate-600 hover:bg-slate-50" title="Cancel edit" onClick={cancelEdit}>
              <X size={16} />
            </button>
          )}
        </div>
        <div className="mt-4 space-y-3">
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Agent URL" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder={editingId ? "API key - leave blank to keep current" : "API key"} value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} required={!editingId} />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder={editingId ? "Action key - leave blank to keep current" : "Action key"} value={form.action_key} onChange={(e) => setForm({ ...form, action_key: e.target.value })} />
          <select className="focus-ring w-full rounded border border-line px-3 py-2" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
            <option value="production">production</option>
            <option value="test">test</option>
            <option value="homelab">homelab</option>
          </select>
          <textarea className="focus-ring min-h-24 w-full rounded border border-line px-3 py-2" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
            {editingId ? <Save size={16} /> : <Plus size={16} />}
            {editingId ? "Save changes" : "Add server"}
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
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
              <span className="rounded border border-line px-2 py-1">{server.environment}</span>
              <span className="rounded border border-line px-2 py-1">API key {server.api_key_configured ? "set" : "missing"}</span>
              <span className="rounded border border-line px-2 py-1">Action key {server.action_key_configured ? "set" : "not set"}</span>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={() => edit(server)}>
                <Pencil size={16} /> Edit
              </button>
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
