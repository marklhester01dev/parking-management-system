"""The one place a parking fee is calculated.

    hours_charged = max(MINIMUM_HOURS, ceil(parked_seconds / 3600))
    total_fee     = hours_charged x HOURLY_RATE
"""
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from flask import current_app

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"   # how times are stored (local time)


def parse_time(value):
    return value if isinstance(value, datetime) else datetime.strptime(value, TIME_FORMAT)


def format_time(value):
    return value.strftime(TIME_FORMAT)


def parked_seconds(entry_time, exit_time):
    """Whole seconds between two times. Raises ValueError if the exit is before the entry."""
    seconds = int((parse_time(exit_time) - parse_time(entry_time)).total_seconds())
    if seconds < 0:
        raise ValueError("Exit time is earlier than entry time.")
    return seconds


def hours_charged(seconds):
    """Round up to the next full hour; never less than the minimum."""
    full_hours = (seconds + 3599) // 3600
    return max(current_app.config["MINIMUM_HOURS"], full_hours)


def calculate_fee(entry_time, exit_time, rate=None):
    """Return (hours_charged, total_fee) for a stay."""
    rate = current_app.config["HOURLY_RATE"] if rate is None else rate
    hours = hours_charged(parked_seconds(entry_time, exit_time))
    fee = (Decimal(str(rate)) * hours).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return hours, float(fee)


def peso(value):
    return f"{current_app.config['CURRENCY_SYMBOL']}{float(value):,.2f}"


def format_duration(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes = rest // 60
    if hours:
        return f"{hours} h {minutes:02d} min"
    return f"{minutes} min" if minutes else "less than 1 min"


def rate_statement():
    """The stated rate, shown wherever a fee appears."""
    minimum = current_app.config["MINIMUM_HOURS"]
    unit = "hour" if minimum == 1 else "hours"
    return (f"{peso(current_app.config['HOURLY_RATE'])} per hour. Parking time is rounded up "
            f"to the next full hour; minimum {minimum} {unit}.")