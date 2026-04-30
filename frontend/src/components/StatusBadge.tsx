type Props = {
  value?: string | null;
};

const styles: Record<string, string> = {
  online: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  running: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  healthy: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-amber-200",
  critical: "bg-red-50 text-red-700 ring-red-200",
  unhealthy: "bg-red-50 text-red-700 ring-red-200",
  offline: "bg-red-50 text-red-700 ring-red-200",
  exited: "bg-slate-100 text-slate-700 ring-slate-200",
  unknown: "bg-slate-100 text-slate-700 ring-slate-200",
  none: "bg-slate-100 text-slate-700 ring-slate-200"
};

export default function StatusBadge({ value }: Props) {
  const normalized = (value || "unknown").toLowerCase();
  return (
    <span className={`inline-flex min-w-16 items-center justify-center rounded px-2 py-1 text-xs font-medium ring-1 ${styles[normalized] || styles.unknown}`}>
      {normalized}
    </span>
  );
}

