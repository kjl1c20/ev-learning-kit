import { CurveMetrics } from "@/lib/api";

export default function MetricsPanel({ metrics }: { metrics: CurveMetrics }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Metric label="10 → 80%" value={`${metrics.time_10_to_80_minutes.toFixed(0)} min`} />
      <Metric label="Energy delivered" value={`${metrics.total_energy_kwh.toFixed(1)} kWh`} />
      <Metric label="Average power" value={`${metrics.avg_power_kw.toFixed(0)} kW`} />
      <Metric label="Peak power" value={`${metrics.peak_power_kw.toFixed(0)} kW`} />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}
