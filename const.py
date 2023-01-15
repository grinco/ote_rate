"""Constants used by ote rates."""
from __future__ import annotations

from typing import Final


DOMAIN: Final = "ote_rate"
NATIVE_UNIT_OF_MEASUREMENT: Final = "EUR/MWh"
DEVICE_CLASS: Final = "monetary"
NEXT_DAY_PREFIX: Final = "next_day_"
NEXT_DAY_AVAILABLE_ATTRIBUTE: Final = "next_day_available"
CONF_CURRENCY: Final = "currency"
CONF_EXCHANGE_RATE: Final = "exchange_rate"
CONF_EXCHANGE_RATE_SENSOR_ID: Final = "exchange_rate_sensor_id"
CONF_CHARGE: Final = "charge"
CURRENCY_EUR: Final = "EUR"
CURRENCY_CZK: Final = "CZK"
DEFAULT_NAME: Final = "OTE rates"
