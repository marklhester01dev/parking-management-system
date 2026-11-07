from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from config import VEHICLE_TYPES
from db import get_db
from services import vehicles as svc

bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")

TYPE_OPTIONS = [(t, t.capitalize()) for t in VEHICLE_TYPES]


def _form(vehicle, values, errors, status=200):
    return render_template(
        "vehicles/form.html", vehicle=vehicle, values=values, errors=errors,
        type_options=TYPE_OPTIONS,
    ), status


@bp.get("")
def list_vehicles():
    return render_template("vehicles/list.html", vehicles=svc.list_all(get_db()))


@bp.route("/new", methods=("GET", "POST"))
def create_vehicle():
    if request.method == "GET":
        return _form(None, {"plate_number": "", "owner_name": "", "vehicle_type": ""}, {})
    db = get_db()
    values, errors = svc.validate(db, request.form)
    if not errors:
        _, errors = svc.create(db, values)
    if errors:
        return _form(None, values, errors, 400)
    flash(f"Vehicle {values['plate_number']} registered.", "success")
    return redirect(url_for("vehicles.list_vehicles"))


@bp.route("/<int:vehicle_id>/edit", methods=("GET", "POST"))
def edit_vehicle(vehicle_id):
    db = get_db()
    vehicle = svc.get(db, vehicle_id)
    if vehicle is None:
        abort(404)
    if request.method == "GET":
        return _form(vehicle, dict(vehicle), {})
    values, errors = svc.validate(db, request.form, vehicle_id)
    if not errors:
        errors = svc.update(db, vehicle_id, values)
    if errors:
        return _form(vehicle, values, errors, 400)
    flash(f"Vehicle {values['plate_number']} updated.", "success")
    return redirect(url_for("vehicles.list_vehicles"))


@bp.post("/<int:vehicle_id>/delete")
def delete_vehicle(vehicle_id):
    db = get_db()
    vehicle = svc.get(db, vehicle_id)
    if vehicle is None:
        abort(404)
    error = svc.delete(db, vehicle_id)
    if error:
        flash(error, "danger")
    else:
        flash(f"Vehicle {vehicle['plate_number']} deleted.", "success")
    return redirect(url_for("vehicles.list_vehicles"))