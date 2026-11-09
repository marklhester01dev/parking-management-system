"""Vehicle entry and exit. Each is ONE database transaction: either every related change
is saved (transaction row + slot status) or none is. Python checks give friendly messages;
the partial unique indexes and CHECK constraints in schema.sql back them up."""
import sqlite3
from datetime import datetime

from db import write_transaction
from services import fees
from services.slots import natural_key


class Rejected(Exception):
    """A business rule refused the action. `field` names the form field to blame, if any."""

    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


_MAX_ID = 2**63 - 1   # SQLite INTEGER limit; larger values raise OverflowError


def _int(value):
    """A usable row id, or None for anything else (text, zero, negative, too large)."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 0 < number <= _MAX_ID else None


# ---- reads -----------------------------------------------------------------

def parkable_vehicles(db):
    """Registered vehicles that are not parked right now."""
    return db.execute(
        """
        SELECT v.vehicle_id, v.plate_number, v.owner_name, v.vehicle_type
          FROM vehicles v
         WHERE v.vehicle_id NOT IN
               (SELECT vehicle_id FROM parking_transactions WHERE status = 'active')
         ORDER BY v.plate_number
        """
    ).fetchall()


def available_slots(db):
    rows = db.execute(
        "SELECT slot_id, slot_number FROM parking_slots WHERE slot_status = 'available'"
    ).fetchall()
    return sorted(rows, key=natural_key)


_ACTIVE_SQL = """
    SELECT t.transaction_id, t.entry_time, v.vehicle_id, v.plate_number, v.owner_name,
           v.vehicle_type, s.slot_id, s.slot_number
      FROM parking_transactions t
      JOIN vehicles v      ON v.vehicle_id = t.vehicle_id
      JOIN parking_slots s ON s.slot_id = t.slot_id
     WHERE t.status = 'active'
"""


def _with_running_fee(row, now):
    item = dict(row)
    seconds = fees.parked_seconds(item["entry_time"], now)
    item["seconds"] = seconds
    item["hours"] = fees.hours_charged(seconds)
    item["fee"] = fees.calculate_fee(item["entry_time"], now)[1]
    return item


def list_active(db, now=None):
    """Active parkings with the time so far and what the fee would be if they left now."""
    now = fees.format_time(now or datetime.now())
    rows = db.execute(_ACTIVE_SQL + " ORDER BY t.entry_time, t.transaction_id").fetchall()
    return [_with_running_fee(r, now) for r in rows]


def get_active(db, transaction_id, now=None):
    """One active parking with its running fee, or None."""
    now = fees.format_time(now or datetime.now())
    row = db.execute(_ACTIVE_SQL + " AND t.transaction_id = ?", (transaction_id,)).fetchone()
    return _with_running_fee(row, now) if row else None


def transaction_status(db, transaction_id):
    """'active', 'completed' or None when it does not exist."""
    row = db.execute(
        "SELECT status FROM parking_transactions WHERE transaction_id = ?", (transaction_id,)
    ).fetchone()
    return row["status"] if row else None


# ---- entry -----------------------------------------------------------------

def enter(db, vehicle_id, slot_id, now=None):
    """Park a vehicle in an available slot. Returns (result, None) or (None, error)."""
    vehicle_id, slot_id = _int(vehicle_id), _int(slot_id)
    entry_time = fees.format_time(now or datetime.now())
    try:
        with write_transaction(db):
            vehicle = db.execute(
                "SELECT vehicle_id, plate_number FROM vehicles WHERE vehicle_id = ?",
                (vehicle_id,),
            ).fetchone()
            if vehicle is None:
                raise Rejected("Choose a registered vehicle.", "vehicle_id")
            slot = db.execute(
                "SELECT slot_id, slot_number, slot_status FROM parking_slots WHERE slot_id = ?",
                (slot_id,),
            ).fetchone()
            if slot is None:
                raise Rejected("Choose an existing slot.", "slot_id")

            parked_in = db.execute(
                "SELECT s.slot_number FROM parking_transactions t "
                "JOIN parking_slots s ON s.slot_id = t.slot_id "
                "WHERE t.vehicle_id = ? AND t.status = 'active'",
                (vehicle_id,),
            ).fetchone()
            if parked_in:
                raise Rejected(
                    f"{vehicle['plate_number']} is already parked in slot "
                    f"{parked_in['slot_number']}.", "vehicle_id")
            if slot["slot_status"] == "occupied":
                raise Rejected(f"Slot {slot['slot_number']} is already occupied.", "slot_id")
            if slot["slot_status"] != "available":
                raise Rejected(f"Slot {slot['slot_number']} is under maintenance.", "slot_id")

            cur = db.execute(
                "INSERT INTO parking_transactions (vehicle_id, slot_id, entry_time, status) "
                "VALUES (?, ?, ?, 'active')",
                (vehicle_id, slot_id, entry_time),
            )
            changed = db.execute(
                "UPDATE parking_slots SET slot_status = 'occupied' "
                "WHERE slot_id = ? AND slot_status = 'available'",
                (slot_id,),
            ).rowcount
            if changed != 1:                       # rolls the INSERT back too
                raise Rejected(f"Slot {slot['slot_number']} is no longer available.", "slot_id")
        return {
            "transaction_id": cur.lastrowid, "plate_number": vehicle["plate_number"],
            "slot_number": slot["slot_number"], "entry_time": entry_time,
        }, None
    except Rejected as exc:
        return None, exc
    except sqlite3.IntegrityError:
        return None, Rejected("The vehicle or slot is already in use. Nothing was saved; "
                              "refresh and try again.")
    except sqlite3.OperationalError:
        return None, Rejected("The database is busy. Nothing was saved; try again.")


# ---- exit ------------------------------------------------------------------

def exit_vehicle(db, transaction_id, now=None):
    """Complete an active parking: exit time, fee, status, and release the slot together.
    Returns (result, None) or (None, error)."""
    exit_time = fees.format_time(now or datetime.now())
    try:
        with write_transaction(db):
            row = db.execute(_ACTIVE_SQL + " AND t.transaction_id = ?",
                             (transaction_id,)).fetchone()
            if row is None:
                raise Rejected("This parking record is not active (it may already have exited).")
            try:
                hours, fee = fees.calculate_fee(row["entry_time"], exit_time)
            except ValueError:
                raise Rejected("Exit time is earlier than entry time. Check the computer clock.")
            seconds = fees.parked_seconds(row["entry_time"], exit_time)

            done = db.execute(
                "UPDATE parking_transactions SET exit_time = ?, total_fee = ?, status = 'completed' "
                "WHERE transaction_id = ? AND status = 'active'",
                (exit_time, fee, transaction_id),
            ).rowcount
            freed = db.execute(
                "UPDATE parking_slots SET slot_status = 'available' WHERE slot_id = ?",
                (row["slot_id"],),
            ).rowcount
            if done != 1 or freed != 1:            # rolls both back
                raise Rejected("This parking record could not be completed. Nothing was saved.")
        return {
            "transaction_id": transaction_id, "plate_number": row["plate_number"],
            "slot_number": row["slot_number"], "entry_time": row["entry_time"],
            "exit_time": exit_time, "seconds": seconds, "hours": hours, "fee": fee,
        }, None
    except Rejected as exc:
        return None, exc
    except sqlite3.IntegrityError:
        return None, Rejected("The exit could not be saved. Nothing was changed; try again.")
    except sqlite3.OperationalError:
        return None, Rejected("The database is busy. Nothing was saved; try again.")