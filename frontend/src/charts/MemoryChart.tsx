import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function MemoryChart({ data }: { data: any[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <XAxis dataKey="created_at" tickFormatter={(value) => new Date(value).toLocaleTimeString()} minTickGap={32} />
        <YAxis domain={[0, 100]} />
        <Tooltip labelFormatter={(value) => new Date(String(value)).toLocaleString()} />
        <Line type="monotone" dataKey="memory_percent" stroke="#16a34a" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

