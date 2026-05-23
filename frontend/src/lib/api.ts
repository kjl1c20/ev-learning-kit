const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Source {
  url?: string;
  title?: string;
  file_name?: string;
  source_type?: string;
  [key: string]: unknown;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export async function askQuestion(query: string, topK = 5): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/api/v1/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

export type VehicleClass = "sedan" | "suv" | "truck" | "van";

export interface CurvePoint {
  soc_pct: number;
  power_kw: number;
}

export interface CurveParameters {
  curve_type: "flat_plateau" | "tapered_ramp" | "stepped";
  initial_power_kw: number;
  peak_power_kw: number;
  peak_soc_start: number;
  peak_soc_end: number;
  taper_end_soc: number;
  tail_power_kw: number;
  chemistry: "NMC" | "LFP";
  voltage_architecture: 400 | 800 | 900;
  reasoning: string;
  steps: [number, number][] | null;
}

export interface CurveMetrics {
  time_10_to_80_minutes: number;
  total_energy_kwh: number;
  avg_power_kw: number;
  peak_power_kw: number;
}

export interface GenerateCurveResponse {
  native_curve: CurvePoint[];
  delivered_curve: CurvePoint[];
  parameters: CurveParameters;
  metrics: CurveMetrics;
  sources: Source[];
}

export interface GenerateCurveRequest {
  vehicle_class: VehicleClass;
  total_battery_capacity_kwh: number;
  usable_battery_capacity_kwh: number;
  vehicle_max_dc_kw: number;
  site_power_kw: number;
}

export async function generateCurve(request: GenerateCurveRequest): Promise<GenerateCurveResponse> {
  const response = await fetch(`${API_URL}/api/v1/generate-curve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}
