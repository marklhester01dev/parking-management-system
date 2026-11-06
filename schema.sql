CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT NOT NULL UNIQUE,
    owner_name   TEXT NOT NULL,
    vehicle_type TEXT NOT NULL
        CHECK (vehicle_type IN ('car', 'motorcycle', 'van', 'truck'))
);

CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number TEXT NOT NULL UNIQUE,
    slot_status TEXT NOT NULL DEFAULT 'available'
        CHECK (slot_status IN ('available', 'occupied', 'maintenance'))
);

CREATE TABLE IF NOT EXISTS parking_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id     INTEGER NOT NULL REFERENCES vehicles(vehicle_id)    ON DELETE RESTRICT,
    slot_id        INTEGER NOT NULL REFERENCES parking_slots(slot_id)  ON DELETE RESTRICT,
    entry_time     TEXT NOT NULL,            -- 'YYYY-MM-DD HH:MM:SS' (local time)
    exit_time      TEXT,
    total_fee      REAL,
    status         TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed')),
    CHECK (
        (status = 'active'    AND exit_time IS NULL     AND total_fee IS NULL) OR
        (status = 'completed' AND exit_time IS NOT NULL AND total_fee IS NOT NULL
                              AND exit_time >= entry_time AND total_fee >= 0)
    )
);

-- Business rules enforced by the database:
-- one active transaction per vehicle, and one per slot.
CREATE UNIQUE INDEX IF NOT EXISTS ux_active_vehicle
    ON parking_transactions(vehicle_id) WHERE status = 'active';
CREATE UNIQUE INDEX IF NOT EXISTS ux_active_slot
    ON parking_transactions(slot_id) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS ix_transactions_status ON parking_transactions(status);