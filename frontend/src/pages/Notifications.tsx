import { Send, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

export default function Notifications() {
  const [channels, setChannels] = useState<any[]>([]);
  const [type, setType] = useState("discord");
  const [name, setName] = useState("");
  const [configText, setConfigText] = useState('{"webhook_url":""}');
  const [message, setMessage] = useState("");

  async function load() {
    setChannels(await api.get("/api/notifications"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post("/api/notifications", { type, name, enabled: true, config: JSON.parse(configText) });
    setName("");
    await load();
  }

  async function test(id: number) {
    const result = await api.post<any>(`/api/notifications/${id}/test`);
    setMessage(result.message);
  }

  async function remove(id: number) {
    await api.del(`/api/notifications/${id}`);
    await load();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={submit}>
        <h2 className="text-lg font-semibold text-ink">Notification Channel</h2>
        <div className="mt-4 space-y-3">
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
          <select className="focus-ring w-full rounded border border-line px-3 py-2" value={type} onChange={(e) => {
            setType(e.target.value);
            setConfigText(e.target.value === "discord" ? '{"webhook_url":""}' : '{"smtp_host":"","smtp_port":587,"smtp_from":"","smtp_to":""}');
          }}>
            <option value="discord">Discord</option>
            <option value="email">Email</option>
          </select>
          <textarea className="focus-ring min-h-36 w-full rounded border border-line px-3 py-2 font-mono text-xs" value={configText} onChange={(e) => setConfigText(e.target.value)} />
          <button className="focus-ring rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">Save channel</button>
        </div>
      </form>

      <div className="space-y-3">
        {message && <div className="rounded border border-line bg-panel px-3 py-2 text-sm text-slate-600">{message}</div>}
        {channels.map((channel) => (
          <div key={channel.id} className="rounded-lg border border-line bg-panel p-4 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-ink">{channel.name}</h3>
                <p className="mt-1 text-sm text-slate-500">{channel.type}</p>
              </div>
              <StatusBadge value={channel.enabled ? "online" : "unknown"} />
            </div>
            <div className="mt-4 flex gap-2">
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-slate-50" onClick={() => test(channel.id)}>
                <Send size={16} /> Test
              </button>
              <button className="focus-ring inline-flex items-center gap-2 rounded border border-red-200 px-3 py-2 text-sm text-red-700 hover:bg-red-50" onClick={() => remove(channel.id)}>
                <Trash2 size={16} /> Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

