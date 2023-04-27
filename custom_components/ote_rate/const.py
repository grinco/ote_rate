"""Constants used by ote rates."""
from __future__ import annotations
from typing import Final

DOMAIN: Final = "ote_rate"
VERSION: Final = "0.2.4"
ATTR_MANUFACTURER: Final = "OTE"
ATTRIBUTION = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh"

MWH: Final = "MWh"
NEXT_DAY_PREFIX: Final = "next_day_"
NEXT_DAY_AVAILABLE_ATTRIBUTE: Final = "next_day_available"
CONF_CURRENCY: Final = "currency"
CONF_EXCHANGE_RATE: Final = "exchange_rate"
CONF_EXCHANGE_RATE_SENSOR_ID: Final = "exchange_rate_sensor_id"
CONF_CHARGE: Final = "charge"
CURRENCY_EUR: Final = "EUR"
CURRENCY_CZK: Final = "CZK"
DEFAULT_OTE_CURRENCY: Final = CURRENCY_EUR
DEFAULT_NAME: Final = "OTE Energy"
COST_RESPONSE_NAME: Final = "Cena (EUR/MWh)"
HOUR_RESPONSE_NAME: Final = "Hodina"
OTE_BASE_URL: Final = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina"
OTE_DENNI_TRH: Final = "denni-trh"
OTE_CHART_DATA_ENDPOINT: Final = "@@chart-data"

SETTINGS_DATA_KEY: Final = "settings"
