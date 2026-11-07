"""Vehicle master data: validation and SQL. Routes call these; templates never do."""
import re
import sqlite3

from config import VEHICLE_TYPES

PLATE_MAX = 12
OWNER_MAX = 100
_PLATE_RE = re.compile(r"[A-Z0-9]+(?:[ -][A-Z0-9]+)*")

PLATE_TAKEN = "This plate number is already registered."


def clean_plate(raw):
    """Trim, collapse inner spaces, uppercase."""
    return " ".join((raw or "").split()).upper()


def clean_owner(raw):
    return " ".join((raw or "").split())


def validate(db, form, vehicle_id=None):
    """Return (clean values, {field: message}). Nothing is written."""
    values = {
        "plate_number": clean_plate(form.get("plate_number")),
        "owner_name": clean_owner(form.get("owner_name")),
        "vehicle_type": (form.get("vehicle_type") or "").strip().lower(),
    }
    errors = {}

    plate = values["plate_number"]
    if not plate:
        errors["plate_number"] = "Plate number is required."
    elif len(plate) > PLATE_MAX:
        errors["plate_number"] = f"Plate number must be {PLATE_MAX} characters or fewer."
    elif not _PLATE_RE.fullmatch(plate):
        errors["plate_number"] = "Use letters, numbers, spaces or hyphens only."
    elif _plate_taken(db, plate, vehicle_id):
        errors["plate_number"] = PLATE_TAKEN

    owner = values["owner_name"]
    if not owner:
        errors["owner_name"] = "Owner name is required."
    elif len(owner) > OWNER_MAX:
        errors["owner_name"] = f"Owner name must be {OWNER_MAX} characters or fewer."
    elif not owner.isprintable():
        errors["owner_name"] = "Owner name contains characters that are not allowed."

    if values["vehicle_type"] not in VEHICLE_TYPES:
        errors["vehicle_type"] = "Choose a vehicle type from the list."

    return values, errors


def _plate_taken(db, plate, vehicle_id):
    row = db.execute(
        "SELECT 1 FROM vehicles WHERE plate_number = ? AND vehicle_id IS NOT ?",
        (plate, vehicle_id),
    ).fetchone()
    return row is not None


def list_all(db):
    """Vehicles with the slot they are parked in now (if any) and their record count."""
    return db.execute(
        """
        SELECT v.vehicle_id, v.plate_number, v.owner_name, v.vehicle_type,
               s.slot_number AS parked_slot,
               (SELECT COUNT(*) FROM parking_transactions t2
                 WHERE t2.vehicle_id = v.vehicle_id) AS history_count
          FROM vehicles v
          LEFT JOIN parking_transactions t
                 ON t.vehicle_id = v.vehicle_id AND t.status = 'active'
          LEFT JOIN parking_slots s ON s.slot_id = t.slot_id
         ORDER BY v.plate_number
        """
    ).fetchall()


def get(db, vehicle_id):
    return db.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,)).fetchone()


def create(db, values):
    """Return (vehicle_id, errors). A lost race on the UNIQUE plate becomes a field error."""
    try:
        with db:
            cur = db.execute(
                "INSERT INTO vehicles (plate_number, owner_name, vehicle_type) VALUES (?, ?, ?)",
                (values["plate_number"], values["owner_name"], values["vehicle_type"]),
            )
        return cur.lastrowid, {}
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc):
            return None, {"plate_number": PLATE_TAKEN}
        raise


def update(db, vehicle_id, values):
    """Return {field: message}; empty means saved."""
    try:
        with db:
            db.execute(
                "UPDATE vehicles SET plate_number = ?, owner_name = ?, vehicle_type = ? "
                "WHERE vehicle_id = ?",
                (values["plate_number"], values["owner_name"], values["vehicle_type"], vehicle_id),
            )
        return {}
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc):
            return {"plate_number": PLATE_TAKEN}
        raise


def delete(db, vehicle_id):
    """Return None when deleted, otherwise a message. Vehicles with any record are kept."""
    try:
        with db:
            used = db.execute(
                "SELECT COUNT(*) FROM parking_transactions WHERE vehicle_id = ?", (vehicle_id,)
            ).fetchone()[0]
            if used:
                return "This vehicle has parking records and cannot be deleted."
            cur = db.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
            if cur.rowcount == 0:
                return "Vehicle not found."
        return None
    except sqlite3.IntegrityError:
        return "This vehicle has parking records and cannot be deleted."