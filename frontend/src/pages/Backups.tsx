import { Download, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Backups() {
  const [backups, setBackups] = useState<any[]>([]);

  async function load() {
    setBackups(await api.get("/api/backups"));
  }

  async function create() {
    await api.post("/api/backups");
    await load();
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Backups</h2>
        <button className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-slate-700" onClick={create}>
          <Plus size={16} /> Create
        </button>
      </div>
      <div className="overflow-hidden rounded-lg border border-line bg-panel shadow-sm">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-normal text-slate-500">
            <tr><th className="px-3 py-3">Filename</th><th className="px-3 py-3">Size</th><th className="px-3 py-3">Created</th><th className="px-3 py-3 text-right">Download</th></tr>
          </thead>
          <tbody className="divide-y divide-line">
            {backups.map((backup) => (
              <tr key={backup.id}>
                <td className="px-3 py-3 font-medium text-ink">{backup.filename}</td>
                <td className="px-3 py-3 text-slate-600">{backup.size_bytes} bytes</td>
                <td className="px-3 py-3 text-slate-600">{new Date(backup.created_at).toLocaleString()}</td>
                <td className="px-3 py-3 text-right">
                  <a className="focus-ring inline-flex items-center gap-2 rounded border border-line px-3 py-2 hover:bg-slate-50" href={`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}/api/backups/${backup.id}/download`}>
                    <Download size={16} /> Download
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

