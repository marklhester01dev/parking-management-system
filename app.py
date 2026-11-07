import os

from flask import Flask, render_template

import db
from routes import parking, slots, vehicles
from services import fees


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")
    app.config["DATABASE"] = os.path.join(app.instance_path, "parking.db")
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    app.add_template_filter(fees.peso, "peso")
    app.add_template_filter(fees.format_duration, "duration")

    app.register_blueprint(parking.bp)
    app.register_blueprint(vehicles.bp)
    app.register_blueprint(slots.bp)

    return app