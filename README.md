<!-- Parking Management System Documentation -->

# Vehicle Parking Management System

IT E04 – Integrative Programming and Technologies 2 · Group 8 · 3rd Year BSIT
Stack: Python · Flask · Jinja/HTML · Tailwind CSS v4 · SQL · SQLite

## Planned layout

```
app.py            app factory, routes
config.py         secret key, hourly rate, vehicle types, slot statuses
db.py             connection, init-db command
schema.sql        tables, constraints, indexes
requirements.txt
routes/           blueprints: parking, vehicles, slots (later: dashboard, history)
services/         business logic and SQL: fees, parking (entry/exit), vehicles, slots
templates/        Jinja pages, _macros.html
static/src/       tailwind.css (@theme tokens, @source, @utility)
static/css/       app.css (built output, gitignored: build it before running)
static/js/        app.js (delete confirmation)
docs/             phases, general rules, changelog, git workflow
```

## Run (available from Phase 1)

```
python -m venv .venv && .venv\Scripts\activate
pip install flask
flask --app app init-db        # add --reset to drop all data first
flask --app app run --debug
```

Styles (build once before the first run, and again after pulling or editing templates/CSS; needs the Tailwind v4 standalone CLI; `app.css` is not in Git):

```
tailwindcss -i static/src/tailwind.css -o static/css/app.css --watch
```
