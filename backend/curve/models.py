from typing import Literal

from pydantic import BaseModel, Field


VehicleClass = Literal["sedan", "suv", "truck", "van"]


class GenerateCurveRequest(BaseModel):
    vehicle_class: VehicleClass
    battery_capacity_kwh: float = Field(gt=0, le=1000)
    vehicle_max_dc_kw: float = Field(gt=0, le=500)
    site_power_kw: float = Field(gt=0, le=500)


class CurveParameters(BaseModel):
    """Native vehicle charge curve parameters chosen by the LLM."""
    curve_type: Literal["flat_plateau", "tapered_ramp", "stepped"] = "tapered_ramp"
    initial_power_kw: float
    peak_power_kw: float
    peak_soc_start: float = Field(ge=0, le=100)
    peak_soc_end: float = Field(ge=0, le=100)
    taper_end_soc: float = Field(ge=0, le=100)
    tail_power_kw: float
    chemistry: Literal["NMC", "LFP"]
    voltage_architecture: Literal[400, 800, 900]
    reasoning: str
    steps: list[list[float]] | None = None  # [[soc_pct, power_kw], ...] required when curve_type="stepped"


class CurvePoint(BaseModel):
    soc_pct: float
    power_kw: float


class Metrics(BaseModel):
    time_10_to_80_minutes: float
    total_energy_kwh: float
    avg_power_kw: float
    peak_power_kw: float


class Source(BaseModel):
    title: str | None = None
    url: str | None = None
    file_name: str | None = None


class GenerateCurveResponse(BaseModel):
    native_curve: list[CurvePoint]
    delivered_curve: list[CurvePoint]
    parameters: CurveParameters
    metrics: Metrics
    sources: list[Source]
