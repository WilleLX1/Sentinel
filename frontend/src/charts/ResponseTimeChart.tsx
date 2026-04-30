import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function ResponseTimeChart({ data }: { data: any[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <XAxis dataKey="created_at" tickFormatter={(value) => new Date(value).toLocaleTimeString()} minTickGap={32} />
        <YAxis />
        <Tooltip labelFormatter={(value) => new Date(String(value)).toLocaleString()} />
        <Line type="monotone" dataKey="response_time_ms" stroke="#7c3aed" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

