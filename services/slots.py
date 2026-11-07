"""Parking slot master data: validation and SQL."""
import re
import sqlite3

from config import MANUAL_SLOT_STATUSES

SLOT_MAX = 10
_SLOT_RE = re.compile(r"[A-Z0-9]+(?:-[A-Z0-9]+)*")

SLOT_TAKEN = "This slot number already exists."


def clean_slot_number(raw):
    return "".join((raw or "").split()).upper()


def natural_key(row):
    """A2 before A10."""
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", row["slot_number"])]


def validate(db, form, slot=None):
    """Return (clean values, {field: message}). `slot` is the existing row when editing.

    An occupied slot keeps its status: only entry/exit (Phase 3) may change it.
    """
    slot_id = slot["slot_id"] if slot else None
    values = {"slot_number": clean_slot_number(form.get("slot_number"))}
    errors = {}

    number = values["slot_number"]
    if not number:
        errors["slot_number"] = "Slot number is required."
    elif len(number) > SLOT_MAX:
        errors["slot_number"] = f"Slot number must be {SLOT_MAX} characters or fewer."
    elif not _SLOT_RE.fullmatch(number):
        errors["slot_number"] = "Use letters, numbers and hyphens only (for example A-01)."
    elif _slot_taken(db, number, slot_id):
        errors["slot_number"] = SLOT_TAKEN

    if slot is not None and slot["slot_status"] == "occupied":
        values["slot_status"] = "occupied"
    else:
        status = (form.get("slot_status") or "available").strip().lower()
        values["slot_status"] = status
        if status not in MANUAL_SLOT_STATUSES:
            errors["slot_status"] = "Choose Available or Maintenance."

    return values, errors


def _slot_taken(db, number, slot_id):
    row = db.execute(
        "SELECT 1 FROM parking_slots WHERE slot_number = ? AND slot_id IS NOT ?",
        (number, slot_id),
    ).fetchone()
    return row is not None


def list_all(db):
    """Slots with the plate parked there now (if any) and their record count."""
    rows = db.execute(
        """
        SELECT s.slot_id, s.slot_number, s.slot_status,
               v.plate_number AS parked_plate,
               (SELECT COUNT(*) FROM parking_transactions t2
                 WHERE t2.slot_id = s.slot_id) AS history_count
          FROM parking_slots s
          LEFT JOIN parking_transactions t
                 ON t.slot_id = s.slot_id AND t.status = 'active'
          LEFT JOIN vehicles v ON v.vehicle_id = t.vehicle_id
        """
    ).fetchall()
    return sorted(rows, key=natural_key)


def get(db, slot_id):
    return db.execute("SELECT * FROM parking_slots WHERE slot_id = ?", (slot_id,)).fetchone()


def create(db, values):
    """Return (slot_id, errors)."""
    try:
        with db:
            cur = db.execute(
                "INSERT INTO parking_slots (slot_number, slot_status) VALUES (?, ?)",
                (values["slot_number"], values["slot_status"]),
            )
        return cur.lastrowid, {}
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc):
            return None, {"slot_number": SLOT_TAKEN}
        raise


def update(db, slot_id, values):
    """Return {field: message}; empty means saved. The status of an occupied slot is
    protected in SQL as well, so a stale form cannot release it."""
    try:
        with db:
            db.execute(
                "UPDATE parking_slots SET slot_number = ?, "
                "slot_status = CASE WHEN slot_status = 'occupied' THEN slot_status ELSE ? END "
                "WHERE slot_id = ?",
                (values["slot_number"], values["slot_status"], slot_id),
            )
        return {}
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc):
            return {"slot_number": SLOT_TAKEN}
        raise


def delete(db, slot_id):
    """Return None when deleted, otherwise a message. Occupied slots and slots with
    any record are kept."""
    try:
        with db:
            slot = db.execute(
                "SELECT slot_status FROM parking_slots WHERE slot_id = ?", (slot_id,)
            ).fetchone()
            if slot is None:
                return "Slot not found."
            if slot["slot_status"] == "occupied":
                return "An occupied slot cannot be deleted."
            used = db.execute(
                "SELECT COUNT(*) FROM parking_transactions WHERE slot_id = ?", (slot_id,)
            ).fetchone()[0]
            if used:
                return "This slot has parking records and cannot be deleted."
            db.execute("DELETE FROM parking_slots WHERE slot_id = ?", (slot_id,))
        return None
    except sqlite3.IntegrityError:
        return "This slot has parking records and cannot be deleted."


def counts(db):
    """Slot totals for the dashboard. total = available + occupied + maintenance."""
    return db.execute(
        """
        SELECT COUNT(*)                                              AS total,
               COALESCE(SUM(slot_status = 'available'), 0)           AS available,
               COALESCE(SUM(slot_status = 'occupied'), 0)            AS occupied,
               COALESCE(SUM(slot_status = 'maintenance'), 0)         AS maintenance
          FROM parking_slots
        """
    ).fetchone()