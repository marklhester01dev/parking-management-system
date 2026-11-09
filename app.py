import os
import sqlite3

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException
from werkzeug.routing import IntegerConverter

import db
from routes import history, parking, slots, vehicles
from services import fees
from services import parking as parking_svc
from services import slots as slots_svc

MAX_ID = 2**63 - 1   # largest INTEGER SQLite stores; a bigger id in a URL is simply "not found"

ERROR_TEXT = {
    400: ("Bad request", "The request could not be understood. Go back and try again."),
    404: ("Page not found", "That page or record does not exist. It may have been deleted."),
    405: ("Action not allowed", "That address cannot be opened this way. Use the buttons and forms in the app."),
    500: ("Something went wrong", "The action could not be completed. Check whether your last change was saved, then try again."),
}


class BoundedInt(IntegerConverter):
    """`<int:...>` that refuses ids SQLite cannot store (they would raise OverflowError)."""

    def __init__(self, map, fixed_digits=0, min=None, max=None, signed=False):
        super().__init__(map, fixed_digits, min, MAX_ID if max is None else max, signed)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")
    app.config["DATABASE"] = os.path.join(app.instance_path, "parking.db")
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    app.url_map.converters["int"] = BoundedInt   # before any route is registered

    @app.route("/")
    def index():
        conn = db.get_db()
        return render_template("index.html", counts=slots_svc.counts(conn),
                               active=parking_svc.list_active(conn))

    app.add_template_filter(fees.peso, "peso")
    app.add_template_filter(fees.format_duration, "duration")

    @app.errorhandler(HTTPException)
    def http_error(exc):
        code = exc.code or 500
        title, message = ERROR_TEXT.get(code, (exc.name, "The request could not be completed."))
        return render_template("errors/error.html", code=code, title=title, message=message), code

    @app.errorhandler(sqlite3.Error)
    def database_error(exc):
        app.logger.exception("Database error")
        return render_template(
            "errors/error.html", code=500, title="Database problem",
            message="The database could not be used and nothing was saved. If this is a new "
                    "setup, run: flask --app app init-db",
        ), 500

    app.register_blueprint(parking.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(vehicles.bp)
    app.register_blueprint(slots.bp)

    return app