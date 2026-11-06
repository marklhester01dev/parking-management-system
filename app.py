import os

from flask import Flask, render_template

import db
from routes import slots, vehicles


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

    app.register_blueprint(vehicles.bp)
    app.register_blueprint(slots.bp)

    return app