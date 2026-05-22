import logging

from backend.config import DB_SECRET_NAME
from backend.utils import get_db_connection

logger = logging.getLogger(__name__)

_conn = None


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = get_db_connection(DB_SECRET_NAME)
        _conn.autocommit = True
    return _conn


def get_profiles_by_class(vehicle_class: str) -> list[dict]:
    with _get_conn().cursor() as cur:
        cur.execute(
            """
            SELECT make, model, trim, model_year, vehicle_class, chemistry,
                   battery_capacity_kwh, voltage_architecture, "peak_dc_power_kW",
                   curve_type, curve_points, source_url, notes
            FROM vehicle_profiles
            WHERE vehicle_class = %s
            """,
            (vehicle_class,),
        )
        columns = [d[0] for d in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
