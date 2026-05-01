import {
  Activity,
  AlertTriangle,
  Bell,
  Boxes,
  DatabaseBackup,
  HeartPulse,
  LayoutDashboard,
  LineChart,
  LogOut,
  ScrollText,
  Server,
  Settings as SettingsIcon,
  ShieldCheck
} from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api, wsUrl } from "./api/client";
import Alerts from "./pages/Alerts";
import Backups from "./pages/Backups";
import Containers from "./pages/Containers";
import Dashboard from "./pages/Dashboard";
import HealthChecks from "./pages/HealthChecks";
import Logs from "./pages/Logs";
import Metrics from "./pages/Metrics";
import Notifications from "./pages/Notifications";
import ServerDetail from "./pages/ServerDetail";
import Servers from "./pages/Servers";
import Settings from "./pages/Settings";
import Admin from "./pages/Admin";
import Actions from "./pages/Actions";

const nav = [
  ["dashboard", "Overview", LayoutDashboard],
  ["servers", "Servers", Server],
  ["containers", "Containers", Boxes],
  ["actions", "Actions", Activity],
  ["logs", "Logs", ScrollText],
  ["metrics", "Metrics", LineChart],
  ["alerts", "Alerts", AlertTriangle],
  ["health", "Health", HeartPulse],
  ["notifications", "Notify", Bell],
  ["settings", "Settings", SettingsIcon],
  ["backups", "Backups", DatabaseBackup],
  ["admin", "Admin", ShieldCheck]
] as const;

function routeFromHash() {
  return window.location.hash.replace(/^#/, "") || "dashboard";
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await api.post("/api/auth/login", { username, password });
      onLogin();
    } catch {
      setError("Invalid username or password");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-slate-100 p-4">
      <form className="w-full max-w-sm rounded-lg border border-line bg-panel p-6 shadow-sm" onSubmit={submit}>
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-ink">Sentinel</h1>
          <p className="mt-1 text-sm text-slate-500">Local infrastructure dashboard</p>
        </div>
        <div className="space-y-3">
          <input className="focus-ring w-full rounded border border-line px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
          <input className="focus-ring w-full rounded border border-line px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
          {error && <p className="text-sm text-red-700">{error}</p>}
          <button className="focus-ring w-full rounded bg-ink px-3 py-2 font-medium text-white hover:bg-slate-700">Sign in</button>
        </div>
      </form>
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [route, setRoute] = useState(routeFromHash());
  const [eventCount, setEventCount] = useState(0);

  async function loadUser() {
    try {
      setUser(await api.get("/api/auth/me"));
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  function navigate(next: string) {
    window.location.hash = next;
    setRoute(next);
  }

  async function logout() {
    await api.post("/api/auth/logout");
    setUser(null);
  }

  useEffect(() => {
    loadUser();
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    if (!user) return;
    const socket = new WebSocket(wsUrl());
    socket.onmessage = () => setEventCount((count) => count + 1);
    return () => socket.close();
  }, [user]);

  if (loading) return <div className="grid min-h-screen place-items-center text-slate-500">Loading Sentinel</div>;
  if (!user) return <Login onLogin={loadUser} />;

  const [kind, serverRaw, containerRaw] = route.split(":");
  const page =
    kind === "servers" ? <Servers navigate={navigate} /> :
    kind === "server" ? <ServerDetail serverId={Number(serverRaw)} navigate={navigate} /> :
    kind === "containers" ? <Containers navigate={navigate} /> :
    kind === "actions" ? <Actions initialServerId={serverRaw ? Number(serverRaw) : undefined} initialContainerId={containerRaw} /> :
    kind === "logs" ? <Logs initialServerId={serverRaw ? Number(serverRaw) : undefined} initialContainerId={containerRaw} /> :
    kind === "metrics" ? <Metrics /> :
    kind === "alerts" ? <Alerts /> :
    kind === "health" ? <HealthChecks /> :
    kind === "notifications" ? <Notifications /> :
    kind === "settings" ? <Settings /> :
    kind === "backups" ? <Backups /> :
    kind === "admin" ? <Admin user={user} /> :
    <Dashboard navigate={navigate} />;

  return (
    <div className="min-h-screen bg-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-panel p-4 lg:block">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-ink">Sentinel</h1>
          <p className="mt-1 text-xs text-slate-500">Events {eventCount}</p>
        </div>
        <nav className="space-y-1">
          {nav.map(([id, label, Icon]) => (
            <button
              key={id}
              className={`focus-ring flex w-full items-center gap-3 rounded px-3 py-2 text-left text-sm ${kind === id ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"}`}
              onClick={() => navigate(id)}
            >
              <Icon size={17} />
              {label}
            </button>
          ))}
        </nav>
        <button className="focus-ring absolute bottom-4 left-4 right-4 flex items-center gap-3 rounded border border-line px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={logout}>
          <LogOut size={17} /> Sign out
        </button>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-panel/95 px-4 py-3 backdrop-blur lg:hidden">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-ink">Sentinel</span>
            <select className="focus-ring rounded border border-line px-2 py-1 text-sm" value={kind} onChange={(event) => navigate(event.target.value)}>
              {nav.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
            </select>
          </div>
        </header>
        <main className="mx-auto max-w-7xl p-4 lg:p-8">
          {page}
        </main>
      </div>
    </div>
  );
}
