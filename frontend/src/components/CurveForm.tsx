"use client";

import { FormEvent, useState } from "react";
import { GenerateCurveRequest, VehicleClass } from "@/lib/api";

interface Props {
  onSubmit: (request: GenerateCurveRequest) => void;
  loading: boolean;
}

export default function CurveForm({ onSubmit, loading }: Props) {
  const [vehicleClass, setVehicleClass] = useState<VehicleClass>("sedan");
  const [capacity, setCapacity] = useState(75);
  const [vehicleMaxDc, setVehicleMaxDc] = useState(250);
  const [sitePower, setSitePower] = useState(150);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    onSubmit({
      vehicle_class: vehicleClass,
      battery_capacity_kwh: capacity,
      vehicle_max_dc_kw: vehicleMaxDc,
      site_power_kw: sitePower,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-5">
      <Field label="Vehicle class">
        <select
          value={vehicleClass}
          onChange={(e) => setVehicleClass(e.target.value as VehicleClass)}
          disabled={loading}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="sedan">Sedan</option>
          <option value="suv">SUV</option>
          <option value="truck">Truck</option>
          <option value="van">Van</option>
        </select>
      </Field>

      <Field label="Battery (kWh)">
        <NumberInput value={capacity} onChange={setCapacity} min={10} max={300} disabled={loading} />
      </Field>

      <Field label="Vehicle max DC (kW)">
        <NumberInput value={vehicleMaxDc} onChange={setVehicleMaxDc} min={10} max={500} disabled={loading} />
      </Field>

      <Field label="Charger power (kW)">
        <NumberInput value={sitePower} onChange={setSitePower} min={1} max={500} disabled={loading} />
      </Field>

      <div className="flex items-end">
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</span>
      {children}
    </label>
  );
}

function NumberInput({
  value,
  onChange,
  min,
  max,
  disabled,
}: {
  value: number;
  onChange: (n: number) => void;
  min: number;
  max: number;
  disabled: boolean;
}) {
  return (
    <input
      type="number"
      min={min}
      max={max}
      step={1}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      disabled={disabled}
      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
}
