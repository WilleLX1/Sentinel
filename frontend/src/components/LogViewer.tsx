type Props = {
  lines: string[];
};

function lineClass(line: string): string {
  const lower = line.toLowerCase();
  if (lower.includes("error") || lower.includes("fatal")) return "text-red-300";
  if (lower.includes("warn")) return "text-amber-200";
  return "text-slate-200";
}

export default function LogViewer({ lines }: Props) {
  return (
    <pre className="h-[520px] overflow-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs leading-5 shadow-sm">
      {lines.map((line, index) => (
        <div key={`${index}-${line.slice(0, 20)}`} className={lineClass(line)}>
          {line}
        </div>
      ))}
      {lines.length === 0 && <span className="text-slate-400">No logs loaded.</span>}
    </pre>
  );
}

