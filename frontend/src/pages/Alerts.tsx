import { useEffect, useState } from "react";
import { api } from "../api/client";
import AlertList, { type Alert } from "../components/AlertList";

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showResolved, setShowResolved] = useState(false);

  async function load() {
    setAlerts(await api.get<Alert[]>(`/api/alerts?resolved=${showResolved}`));
  }

  useEffect(() => {
    load();
  }, [showResolved]);

  async function resolve(id: number) {
    await api.post(`/api/alerts/${id}/resolve`);
    await load();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">Alerts</h2>
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" checked={showResolved} onChange={(e) => setShowResolved(e.target.checked)} />
          Resolved
        </label>
      </div>
      <AlertList alerts={alerts} onResolve={resolve} />
    </div>
  );
}

