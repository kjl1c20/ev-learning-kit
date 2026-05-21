import { CurveParameters } from "@/lib/api";

export default function ReasoningPanel({ parameters }: { parameters: CurveParameters }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex flex-wrap gap-2">
        <Tag label={parameters.chemistry} />
        <Tag label={`${parameters.voltage_architecture}V`} />
        <Tag label={`Peak ${parameters.peak_power_kw.toFixed(0)} kW`} />
      </div>

      <p className="text-sm leading-relaxed text-gray-800">{parameters.reasoning}</p>
    </div>
  );
}

function Tag({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
      {label}
    </span>
  );
}
