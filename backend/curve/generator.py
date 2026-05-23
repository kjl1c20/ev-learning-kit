import json
import logging
import re

from backend.curve.math import clip_to_site_power, compute_metrics, generate_native_curve
from backend.curve.models import (
    CurveParameters,
    GenerateCurveRequest,
    GenerateCurveResponse,
    Source,
)
from backend.curve.profiles_repository import get_profiles_by_class
from backend.rag.generator import generate_response
from backend.rag.retrieval import retrieve_relevant_chunks

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert EV charging engineer with deep knowledge of battery \
management systems, DC fast charging behaviour, and vehicle powertrain architecture. \
Given a vehicle class, battery capacity, and reference vehicles with real curve data, \
your job is to generate realistic NATIVE charge curve parameters for a hypothetical \
vehicle of that class.

The curve describes the vehicle's MAXIMUM charging capability. Charging power limits \
are applied separately — ignore them when choosing parameters.

You MUST follow the reasoning steps before producing output, then output ONLY a \
single JSON object. No prose, no code fences, no commentary outside the JSON.
"""

USER_PROMPT_TEMPLATE = """### VEHICLE TO MODEL ###
- Class: {vehicle_class}
- Battery capacity: {battery_capacity_kwh} kWh
- Vehicle max DC charging power: {vehicle_max_dc_kw} kW

The user has specified the vehicle's max DC charging power. You MUST set
peak_power_kw to exactly {vehicle_max_dc_kw}. Your job is to pick the curve
SHAPE that matches a realistic vehicle of this class with this peak power.

### REFERENCE VEHICLES (real empirical curve data) ###
{reference_profiles}

### DOMAIN KNOWLEDGE ###
{rag_context}

### REASONING STEPS (complete before outputting JSON) ###
Step 1 — Identify the closest reference vehicle by class, chemistry, voltage, and peak power.
Step 2 — Determine chemistry (NMC vs LFP) and how it affects taper shape: NMC tapers earlier and steeper; LFP holds power longer and charges to 100% routinely.
Step 3 — Determine voltage architecture effect: 800V/900V systems sustain peak power over a wider SOC range than 400V.
Step 4 — Decide curve_type based on the closest reference vehicle's curve_type:
  - "stepped"      → reference has flat plateaus with abrupt power drops at specific SOC thresholds (typical of NMC BMS steps)
  - "flat_plateau" → reference has a wide flat peak with minimal taper
  - "tapered_ramp" → reference has a smooth ramp-up and gradual taper
Step 5 — Set peak_soc_start and peak_soc_end based on the above, referencing the closest curve shape from the reference vehicles.
Step 6 — Set taper_end_soc and tail_power_kw consistent with the class and chemistry.
Step 7 — If curve_type is "stepped", derive the steps breakpoints by scaling the closest reference vehicle's curve_points so that the peak power equals {vehicle_max_dc_kw}. Output them as [[soc_pct, power_kw], ...].
Step 8 — Write the reasoning field naming the closest reference vehicle explicitly.

Output JSON with this exact schema:
{{
  "curve_type": "flat_plateau" or "tapered_ramp" or "stepped",
  "initial_power_kw": <power at 0% SOC, typically 30-50% of peak>,
  "peak_power_kw": {vehicle_max_dc_kw},
  "peak_soc_start": <SOC % where flat peak begins>,
  "peak_soc_end": <SOC % where flat peak ends and taper starts>,
  "taper_end_soc": <SOC % where main taper ends>,
  "tail_power_kw": <power at taper_end_soc>,
  "chemistry": "NMC" or "LFP",
  "voltage_architecture": 400 or 800 or 900,
  "reasoning": "<2-3 sentences naming the closest reference vehicle, explaining chemistry and voltage architecture choices, and justifying the curve shape>",
  "steps": [[soc_pct, power_kw], ...] if curve_type is "stepped", else null
}}
"""


def run_curve_generation(request: GenerateCurveRequest) -> GenerateCurveResponse:
    logger.info(
        "Generating curve for class=%s capacity=%skWh max_dc=%skW site=%skW",
        request.vehicle_class, request.battery_capacity_kwh,
        request.vehicle_max_dc_kw, request.site_power_kw,
    )

    rag_query = f"charge curve for {request.vehicle_class} battery chemistry voltage architecture"
    rag_chunks = retrieve_relevant_chunks(rag_query, top_k=4)
    reference_profiles = get_profiles_by_class(request.vehicle_class)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        vehicle_class=request.vehicle_class,
        battery_capacity_kwh=request.battery_capacity_kwh,
        vehicle_max_dc_kw=request.vehicle_max_dc_kw,
        reference_profiles=_format_profiles(reference_profiles),
        rag_context=_format_rag_chunks(rag_chunks),
    )

    raw_response = generate_response(SYSTEM_PROMPT, user_prompt)
    params = _parse_parameters(raw_response)

    native_curve = generate_native_curve(params)
    delivered_curve = clip_to_site_power(native_curve, request.site_power_kw)
    metrics = compute_metrics(delivered_curve, request.battery_capacity_kwh)

    sources = [Source(**{k: v for k, v in chunk["metadata"].items() if k in {"title", "url", "file_name"}}) for chunk in rag_chunks]

    return GenerateCurveResponse(
        native_curve=native_curve,
        delivered_curve=delivered_curve,
        parameters=params,
        metrics=metrics,
        sources=sources,
    )


def _format_profiles(profiles: list[dict]) -> str:
    if not profiles:
        return "(no reference vehicles available for this class)"
    return json.dumps([
        {
            "model": " ".join(filter(None, [p["make"], p["model"], p.get("trim"), str(p["model_year"])])),
            "chemistry": p["chemistry"],
            "voltage": p["voltage_architecture"],
            "capacity_kwh": float(p["battery_capacity_kwh"]),
            "peak_kw": float(p["peak_dc_power_kW"]),
            "curve_type": p["curve_type"],
            "curve_points": p["curve_points"],
            "notes": p["notes"],
        }
        for p in profiles
    ], indent=2)


def _format_rag_chunks(chunks: list[dict]) -> str:
    return "\n\n".join(chunk["document"][:600] for chunk in chunks)


def _parse_parameters(raw: str) -> CurveParameters:
    """Extract JSON from the LLM response, tolerant to stray text or code fences."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response: {raw[:200]}")
    return CurveParameters(**json.loads(match.group(0)))
