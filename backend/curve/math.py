from backend.curve.models import CurveParameters, CurvePoint, Metrics


def generate_native_curve(params: CurveParameters, soc_step: int = 1) -> list[CurvePoint]:
    """
    Build the vehicle's native charge curve from LLM parameters.

    Four regions:
      [0, peak_soc_start)        : linear ramp from initial_power → peak_power
      [peak_soc_start, peak_soc_end] : flat at peak_power
      (peak_soc_end, taper_end_soc]  : linear taper from peak_power → tail_power
      (taper_end_soc, 100]       : linear decline from tail_power → tail_power * 0.2
    """
    points = []
    final_power = params.tail_power_kw * 0.2

    for soc in range(0, 101, soc_step):
        if soc <= params.peak_soc_start:
            power = _interp(soc, 0, params.peak_soc_start, params.initial_power_kw, params.peak_power_kw)
        elif soc <= params.peak_soc_end:
            power = params.peak_power_kw
        elif soc <= params.taper_end_soc:
            power = _interp(soc, params.peak_soc_end, params.taper_end_soc, params.peak_power_kw, params.tail_power_kw)
        else:
            power = _interp(soc, params.taper_end_soc, 100, params.tail_power_kw, final_power)
        points.append(CurvePoint(soc_pct=soc, power_kw=round(power, 1)))

    return points


def clip_to_site_power(curve: list[CurvePoint], site_power_kw: float) -> list[CurvePoint]:
    return [
        CurvePoint(soc_pct=p.soc_pct, power_kw=min(p.power_kw, site_power_kw))
        for p in curve
    ]


def compute_metrics(delivered_curve: list[CurvePoint], capacity_kwh: float) -> Metrics:
    return Metrics(
        time_10_to_80_minutes=round(_charge_time_minutes(delivered_curve, capacity_kwh, 10, 80), 1),
        total_energy_kwh=round(_total_energy_kwh(delivered_curve, capacity_kwh), 1),
        avg_power_kw=round(_average_power_kw(delivered_curve, capacity_kwh), 1),
        peak_power_kw=round(max(p.power_kw for p in delivered_curve), 1),
    )


def _interp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def _charge_time_minutes(curve: list[CurvePoint], capacity_kwh: float, start_soc: float, end_soc: float) -> float:
    """
    Integrate dt = dE / P across the SOC range, assuming linear power between points.
    Returns minutes.
    """
    total_hours = 0.0
    for a, b in zip(curve, curve[1:]):
        seg_start = max(a.soc_pct, start_soc)
        seg_end = min(b.soc_pct, end_soc)
        if seg_end <= seg_start:
            continue

        # Power interpolated to segment endpoints
        p_start = _interp(seg_start, a.soc_pct, b.soc_pct, a.power_kw, b.power_kw)
        p_end = _interp(seg_end, a.soc_pct, b.soc_pct, a.power_kw, b.power_kw)
        avg_power = (p_start + p_end) / 2

        energy_kwh = (seg_end - seg_start) / 100 * capacity_kwh
        total_hours += energy_kwh / avg_power if avg_power > 0 else 0

    return total_hours * 60


def _total_energy_kwh(curve: list[CurvePoint], capacity_kwh: float) -> float:
    return (curve[-1].soc_pct - curve[0].soc_pct) / 100 * capacity_kwh


def _average_power_kw(curve: list[CurvePoint], capacity_kwh: float) -> float:
    total_minutes = _charge_time_minutes(curve, capacity_kwh, curve[0].soc_pct, curve[-1].soc_pct)
    if total_minutes == 0:
        return 0.0
    total_energy = _total_energy_kwh(curve, capacity_kwh)
    return total_energy / (total_minutes / 60)
