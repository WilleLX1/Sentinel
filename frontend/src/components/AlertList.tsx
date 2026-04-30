import StatusBadge from "./StatusBadge";

export type Alert = {
  id: number;
  server_id: number;
  severity: string;
  title: string;
  message: string;
  source: string;
  resolved: boolean;
  created_at: string;
};

export default function AlertList({ alerts, onResolve }: { alerts: Alert[]; onResolve?: (id: number) => void }) {
  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div key={alert.id} className="rounded-lg border border-line bg-panel p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <StatusBadge value={alert.severity} />
                <span className="text-xs uppercase tracking-normal text-slate-500">{alert.source}</span>
              </div>
              <h3 className="mt-2 font-semibold text-ink">{alert.title}</h3>
              <p className="mt-1 text-sm text-slate-600">{alert.message}</p>
            </div>
            {onResolve && !alert.resolved && (
              <button className="focus-ring rounded border border-line px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => onResolve(alert.id)}>
                Resolve
              </button>
            )}
          </div>
        </div>
      ))}
      {alerts.length === 0 && <div className="rounded-lg border border-line bg-panel p-6 text-center text-slate-500">No alerts.</div>}
    </div>
  );
}

