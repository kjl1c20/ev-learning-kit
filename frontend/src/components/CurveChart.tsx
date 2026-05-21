"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CurvePoint } from "@/lib/api";

interface Props {
  nativeCurve: CurvePoint[];
  deliveredCurve: CurvePoint[];
}

export default function CurveChart({ nativeCurve, deliveredCurve }: Props) {
  const data = nativeCurve.map((p, i) => ({
    soc: p.soc_pct,
    native: p.power_kw,
    delivered: deliveredCurve[i]?.power_kw ?? null,
  }));

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="soc"
            label={{ value: "State of Charge (%)", position: "insideBottom", offset: -5, style: { fontSize: 12, fill: "#6b7280" } }}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />
          <YAxis
            label={{ value: "Power (kW)", angle: -90, position: "insideLeft", style: { fontSize: 12, fill: "#6b7280" } }}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(0)} kW`}
            labelFormatter={(label) => `SOC ${label}%`}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line
            type="monotone"
            dataKey="native"
            name="Vehicle native"
            stroke="#9ca3af"
            strokeDasharray="5 5"
            dot={false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="delivered"
            name="Actual (after site limit)"
            stroke="#2563eb"
            dot={false}
            strokeWidth={2.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
