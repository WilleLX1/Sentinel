import type { LucideIcon } from "lucide-react";

type Props = {
  title: string;
  value: string | number;
  detail?: string;
  icon: LucideIcon;
};

export default function MetricCard({ title, value, detail, icon: Icon }: Props) {
  return (
    <div className="rounded-lg border border-line bg-panel p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-normal text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
        </div>
        <div className="grid h-9 w-9 place-items-center rounded border border-line bg-slate-50 text-slate-600">
          <Icon size={18} />
        </div>
      </div>
      {detail && <p className="mt-2 text-sm text-slate-500">{detail}</p>}
    </div>
  );
}

