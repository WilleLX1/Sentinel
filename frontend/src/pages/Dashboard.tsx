import { AlertTriangle, Boxes, Monitor, Server } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import AlertList, { type Alert } from "../components/AlertList";
import MetricCard from "../components/MetricCard";
import ServerCard from "../components/ServerCard";

type Overview = {
  summary: {
    total_servers: number;
    online_servers: number;
    offline_servers: number;
    running_containers: number;
    unhealthy_containers: number;
    active_alerts: number;
    critical_alerts: number;
  };
  servers: any[];
  alerts: Alert[];
};

export default function Dashboard({ navigate }: { navigate: (route: string) => void }) {
  const [overview, setOverview] = useState<Overview | null>(null);

  async function load() {
    setOverview(await api.get<Overview>("/api/overview"));
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 15000);
    return () => window.clearInterval(timer);
  }, []);

  const summary = overview?.summary;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Servers" value={summary?.total_servers ?? 0} detail={`${summary?.online_servers ?? 0} online`} icon={Server} />
        <MetricCard title="Containers" value={summary?.running_containers ?? 0} detail={`${summary?.unhealthy_containers ?? 0} unhealthy`} icon={Boxes} />
        <MetricCard title="Alerts" value={summary?.active_alerts ?? 0} detail={`${summary?.critical_alerts ?? 0} critical`} icon={AlertTriangle} />
        <MetricCard title="Offline" value={summary?.offline_servers ?? 0} detail="Agent reachability" icon={Monitor} />
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink">Servers</h2>
          <button className="focus-ring rounded border border-line px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => navigate("servers")}>
            Manage
          </button>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {(overview?.servers || []).map((server) => (
            <ServerCard key={server.id} server={server} onOpen={(id) => navigate(`server:${id}`)} />
          ))}
          {overview?.servers?.length === 0 && <div className="rounded-lg border border-line bg-panel p-6 text-center text-slate-500">No servers configured.</div>}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-ink">Recent Alerts</h2>
        <AlertList alerts={overview?.alerts || []} />
      </section>
    </div>
  );
}

