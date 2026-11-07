from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import get_db
from services import fees
from services import parking as svc

bp = Blueprint("parking", __name__, url_prefix="/parking")


def _page(values=None, errors=None, status=200):
    db = get_db()
    return render_template(
        "parking/index.html",
        vehicle_options=[
            (str(v["vehicle_id"]),
             f"{v['plate_number']} ({v['owner_name']}, {v['vehicle_type'].capitalize()})")
            for v in svc.parkable_vehicles(db)],
        slot_options=[(str(s["slot_id"]), s["slot_number"]) for s in svc.available_slots(db)],
        active=svc.list_active(db),
        values=values or {"vehicle_id": "", "slot_id": ""},
        errors=errors or {},
        rate_text=fees.rate_statement(),
    ), status


@bp.get("")
def index():
    return _page()


@bp.post("/entry")
def enter():
    values = {"vehicle_id": request.form.get("vehicle_id", ""),
              "slot_id": request.form.get("slot_id", "")}
    result, error = svc.enter(get_db(), values["vehicle_id"], values["slot_id"])
    if error:
        if error.field in values:
            return _page(values, {error.field: str(error)}, 400)
        flash(str(error), "danger")
        return _page(values, status=400)
    flash(f"{result['plate_number']} entered slot {result['slot_number']} at "
          f"{result['entry_time'][11:16]}.", "success")
    return redirect(url_for("parking.index"))


@bp.route("/<int:transaction_id>/exit", methods=("GET", "POST"))
def exit_vehicle(transaction_id):
    db = get_db()
    if svc.transaction_status(db, transaction_id) is None:
        abort(404)

    if request.method == "POST":
        result, error = svc.exit_vehicle(db, transaction_id)
        if error:
            flash(str(error), "danger")
        else:
            flash(f"{result['plate_number']} left slot {result['slot_number']}. Parked "
                  f"{fees.format_duration(result['seconds'])}, {result['hours']} "
                  f"{'hour' if result['hours'] == 1 else 'hours'} charged. "
                  f"Total {fees.peso(result['fee'])}.", "success")
        return redirect(url_for("parking.index"))

    parking = svc.get_active(db, transaction_id)
    if parking is None:
        flash("This parking record is not active (it may already have exited).", "danger")
        return redirect(url_for("parking.index"))
    return render_template("parking/exit.html", parking=parking,
                           now=fees.format_time(datetime.now()), rate_text=fees.rate_statement())