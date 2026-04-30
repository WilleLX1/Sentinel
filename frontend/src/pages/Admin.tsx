import { ShieldCheck } from "lucide-react";

export default function Admin({ user }: { user: any }) {
  return (
    <div className="rounded-lg border border-line bg-panel p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded border border-line bg-slate-50 text-slate-600">
          <ShieldCheck size={20} />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-ink">{user?.username}</h2>
          <p className="text-sm text-slate-500">{user?.is_admin ? "admin" : "user"}</p>
        </div>
      </div>
    </div>
  );
}

