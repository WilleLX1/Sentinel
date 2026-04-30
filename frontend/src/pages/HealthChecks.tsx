import { Play, Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

const empty = { server_id: "", name: "", type: "http", target: "", expected_status: 200, timeout_seconds: 5, enabled: true };

export default function HealthChecks() {
  const [servers, setServers] = useState<any[]>([]);
  const [checks, setChecks] = useState<any[]>([]);
  const [form, setForm] = useState<any>(empty);
  const [results, setResults] = useState<Record<number, any>>({});

  async function load() {
    setServers(await api.get("/api/servers"));
    setChecks(await api.get("/api/health-checks"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post("/api/health-checks", { ...form, server_id: Number(form.server_id) });
    setForm(empty);
    await load();
  }

  async function run(id: number) {
    const result = await api.post<any>(`/api/health-checks/${id}/run`);
    setResults({ ...results, [id]: result });
  }

  async function remove(id: number) {
    await api.del(`/api/health-checks/${id}`);
    await load();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={submit}>
        <h2 className="text-lg font-semibold text-ink">Health Check</h2>
        <div className="mt-4 space-y-3">
          <select className="focus-ring w-full rounded border border-line px-3 py-2" value={form.server_id} onChange={(e) => setForm({ ...form, server_id: e.target.value })} required>
            <option value="">Server</option>
            {servers.map((server) => <option key={server.id} value={server.id}>{server.name}</option>)}
          </select>
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <select className="focus-ring w-full rounded border border-line px-3 py-2" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
            <option value="http">HTTP</option>
            <option value="tcp">TCP</option>
            <option value="ssl">SSL</option>
          </select>
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Target" value={form.target} onChange={(e) => setForm({ ...form, target: e.target.value })} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" type="number" value={form.expected_status} onChange={(e) => setForm({ ...form, expected_status: Number(e.target.value) })} />
          <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
            <Plus size={16} /> Add check
          </button>
        </div>
      </form>

      <div className="space-y-3">
        {checks.map((check) => (
          <div key={check.id} className="rounded-lg border border-line bg-panel p-4 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-ink">{check.name}</h3>
                <p className="mt-1 text-sm text-slate-500">{check.type} {check.target}</p>
                {results[check.id] && <p className="mt-2 text-sm text-slate-600">{results[check.id].message}</p>}
              </div>
              <StatusBadge value={results[check.id] ? (results[check.id].success ? "healthy" : "critical") : check.enabled ? "running" : "unknown"} />
            </div>
            <div className="mt-4 flex gap-2">
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={() => run(check.id)}>
                <Play size={16} /> Run
              </button>
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-red-200 px-3 py-2 text-sm text-red-700 hover:bg-red-50" onClick={() => remove(check.id)}>
                <Trash2 size={16} /> Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

