import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")

# Parking fee (Phase 3): HOURLY_RATE per hour, duration rounded UP to the next full hour,
# minimum 1 hour. Rounding decided 2026-11-07; amount and minimum to be confirmed (docs/phases.md).
HOURLY_RATE = 20.00

# Must match the CHECK constraints in schema.sql.
VEHICLE_TYPES = ("car", "motorcycle", "van", "truck")
SLOT_STATUSES = ("available", "occupied", "maintenance")
# Statuses an operator may set by hand. 'occupied' is set only by entry/exit (Phase 3).
MANUAL_SLOT_STATUSES = ("available", "maintenance")

# Fee display and rule (Phase 3). Formula: max(MINIMUM_HOURS, ceil(hours)) x HOURLY_RATE.
CURRENCY_SYMBOL = "\u20b1"
MINIMUM_HOURS = 1