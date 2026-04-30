import { Save } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";

export default function Settings() {
  const [settings, setSettings] = useState<any>(null);
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");

  async function load() {
    setSettings(await api.get("/api/settings"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.put("/api/settings", { key, value });
    setKey("");
    setValue("");
    await load();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="rounded-lg border border-line bg-panel p-4 shadow-sm" onSubmit={submit}>
        <h2 className="text-lg font-semibold text-ink">App Setting</h2>
        <div className="mt-4 space-y-3">
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Key" value={key} onChange={(e) => setKey(e.target.value)} required />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" placeholder="Value" value={value} onChange={(e) => setValue(e.target.value)} required />
          <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
            <Save size={16} /> Save
          </button>
        </div>
      </form>
      <div className="rounded-lg border border-line bg-panel p-4 shadow-sm">
        <h3 className="font-semibold text-ink">Runtime</h3>
        <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
          <div><dt className="text-slate-500">Poll interval</dt><dd className="font-medium">{settings?.runtime?.poll_interval_seconds}s</dd></div>
          <div><dt className="text-slate-500">Retention</dt><dd className="font-medium">{settings?.runtime?.metric_retention_days} days</dd></div>
          <div><dt className="text-slate-500">Discord env</dt><dd className="font-medium">{String(settings?.runtime?.notifications?.discord_env_configured)}</dd></div>
          <div><dt className="text-slate-500">SMTP env</dt><dd className="font-medium">{String(settings?.runtime?.notifications?.smtp_env_configured)}</dd></div>
        </dl>
        <h3 className="mt-6 font-semibold text-ink">Stored Settings</h3>
        <div className="mt-3 divide-y divide-line rounded border border-line">
          {(settings?.settings || []).map((row: any) => (
            <div key={row.key} className="grid grid-cols-2 gap-3 px-3 py-2 text-sm">
              <span className="font-medium text-ink">{row.key}</span>
              <span className="text-slate-600">{row.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

