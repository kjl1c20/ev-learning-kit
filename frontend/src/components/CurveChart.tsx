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
  onExport: () => void;
}

export default function CurveChart({ nativeCurve, deliveredCurve, onExport }: Props) {
  const data = nativeCurve.map((p, i) => ({
    soc: p.soc_pct,
    native: p.power_kw,
    delivered: deliveredCurve[i]?.power_kw ?? null,
  }));

  return (
    <div className="relative rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <button
        onClick={onExport}
        className="absolute right-4 top-4 flex items-center gap-1.5 rounded-md border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-600 shadow-sm hover:bg-gray-50 transition-colors z-10"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
        </svg>
        Export JSON
      </button>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="soc"
            ticks={[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]}
            label={{ value: "State of Charge (%)", position: "insideBottom", offset: -15, style: { fontSize: 12, fill: "#6b7280" } }}
            tick={{ fontSize: 10, fill: "#6b7280" }}
          />
          <YAxis
            label={{ value: "Power (kW)", angle: -90, position: "insideLeft", style: { fontSize: 12, fill: "#6b7280" } }}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />
          <Tooltip
            formatter={(value) => [typeof value === 'number' ? `${value.toFixed(0)} kW` : value]}
            labelFormatter={(label) => `SOC ${label}%`}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Legend verticalAlign="top" wrapperStyle={{ fontSize: 12, paddingBottom: 8 }} />
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
            name="Actual (after charger limit)"
            stroke="#2563eb"
            dot={false}
            strokeWidth={2.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
