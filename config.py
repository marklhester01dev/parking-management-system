import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")

# Parking fee (Phase 3): HOURLY_RATE per hour, rounded up, minimum 1 hour.
HOURLY_RATE = 20.00

# Must match the CHECK constraints in schema.sql.
VEHICLE_TYPES = ("car", "motorcycle", "van", "truck")
SLOT_STATUSES = ("available", "occupied", "maintenance")
# Statuses an operator may set by hand. 'occupied' is set only by entry/exit (Phase 3).
MANUAL_SLOT_STATUSES = ("available", "maintenance")