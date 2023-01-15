from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from .const import (
    CONF_CURRENCY,
    DOMAIN,
    CONF_EXCHANGE_RATE,
    CONF_EXCHANGE_RATE_SENSOR_ID,
    CURRENCY_CZK,
    CURRENCY_EUR,
    CONF_CHARGE,
    DEFAULT_NAME,
)

"""OTE Rate sensor integration."""


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    config = entry.options
    name = config[CONF_NAME]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][name] = entry.data

    # Forward the setup to the sensor platform.

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
