from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import get_db
from services import slots as svc

bp = Blueprint("slots", __name__, url_prefix="/slots")

STATUS_OPTIONS = [("available", "Available"), ("maintenance", "Maintenance")]
OCCUPIED_OPTIONS = [("occupied", "Occupied")]


def _form(slot, values, errors, status=200):
    locked = slot is not None and slot["slot_status"] == "occupied"
    return render_template(
        "slots/form.html", slot=slot, values=values, errors=errors, locked=locked,
        status_options=OCCUPIED_OPTIONS if locked else STATUS_OPTIONS,
    ), status


@bp.get("")
def list_slots():
    return render_template("slots/list.html", slots=svc.list_all(get_db()))


@bp.route("/new", methods=("GET", "POST"))
def create_slot():
    if request.method == "GET":
        return _form(None, {"slot_number": "", "slot_status": "available"}, {})
    db = get_db()
    values, errors = svc.validate(db, request.form)
    if not errors:
        _, errors = svc.create(db, values)
    if errors:
        return _form(None, values, errors, 400)
    flash(f"Slot {values['slot_number']} created.", "success")
    return redirect(url_for("slots.list_slots"))


@bp.route("/<int:slot_id>/edit", methods=("GET", "POST"))
def edit_slot(slot_id):
    db = get_db()
    slot = svc.get(db, slot_id)
    if slot is None:
        abort(404)
    if request.method == "GET":
        return _form(slot, dict(slot), {})
    values, errors = svc.validate(db, request.form, slot)
    if not errors:
        errors = svc.update(db, slot_id, values)
    if errors:
        return _form(slot, values, errors, 400)
    flash(f"Slot {values['slot_number']} updated.", "success")
    return redirect(url_for("slots.list_slots"))


@bp.post("/<int:slot_id>/delete")
def delete_slot(slot_id):
    db = get_db()
    slot = svc.get(db, slot_id)
    if slot is None:
        abort(404)
    error = svc.delete(db, slot_id)
    if error:
        flash(error, "danger")
    else:
        flash(f"Slot {slot['slot_number']} deleted.", "success")
    return redirect(url_for("slots.list_slots"))