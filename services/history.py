"""Completed parkings and plate search. Read-only: nothing here writes."""
from services import fees
from services.vehicles import PLATE_MAX, clean_plate

_COMPLETED_SQL = """
    SELECT t.transaction_id, v.plate_number, v.owner_name, s.slot_number,
           t.entry_time, t.exit_time, t.total_fee
      FROM parking_transactions t
      JOIN vehicles v      ON v.vehicle_id = t.vehicle_id
      JOIN parking_slots s ON s.slot_id = t.slot_id
     WHERE t.status = 'completed'
"""
_PLATE_FILTER_SQL = " AND v.plate_number LIKE ? ESCAPE '\\'"
_ORDER_SQL = " ORDER BY t.exit_time DESC, t.transaction_id DESC"


def clean_query(raw):
    """Return (search text, error message or None)."""
    q = clean_plate(raw)
    if len(q) > PLATE_MAX:
        return q, f"Plate number must be {PLATE_MAX} characters or fewer."
    return q, None


def _like_pattern(q):
    """Contains-match; % and _ typed by the user are searched literally."""
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def completed(db, q=""):
    """Completed parkings, newest exit first, optionally only plates containing `q`."""
    if q:
        rows = db.execute(_COMPLETED_SQL + _PLATE_FILTER_SQL + _ORDER_SQL,
                          (_like_pattern(q),)).fetchall()
    else:
        rows = db.execute(_COMPLETED_SQL + _ORDER_SQL).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["seconds"] = fees.parked_seconds(item["entry_time"], item["exit_time"])
        items.append(item)
    return items