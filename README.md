<!-- Parking Management System Documentation -->

# Vehicle Parking Management System

IT E04 – Integrative Programming and Technologies 2 · Group 8 · 3rd Year BSIT
Stack: Python · Flask · Jinja/HTML · Tailwind CSS v4 · SQL · SQLite

## Docs

| File                    | Purpose                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `docs/phases.md`        | Build plan by phase: scope, tasks, done-when, rubric mapping      |
| `docs/general-rules.md` | Rules for every change (backend + frontend)                       |
| `docs/changelog.md`     | Log of every change, with backend impact (schema, routes, fields) |

## Planned layout

```
app.py            app factory, routes
config.py         secret key, hourly rate, vehicle types, slot statuses
db.py             connection, init-db command
schema.sql        tables, constraints, indexes
requirements.txt
services/         business logic (entry, exit, fee)
templates/        Jinja pages, _macros.html
static/src/       tailwind.css (@theme tokens, @source, @utility)
static/css/       app.css (built output, committed)
static/js/        optional client-side helpers
docs/
```

## Run (available from Phase 1)

```
python -m venv .venv && .venv\Scripts\activate
pip install flask
flask --app app init-db        # add --reset to drop all data first
flask --app app run --debug
```

Styles (only when editing templates/CSS; needs the Tailwind v4 standalone CLI):

```
tailwindcss -i static/src/tailwind.css -o static/css/app.css --watch
```

## Zips

One zip per finished phase: `parking-system-phaseN.zip`. Zip content = whole project folder, docs updated.
