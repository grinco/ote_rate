from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .const import (
    CONF_CURRENCY,
    DOMAIN,
    CONF_EXCHANGE_RATE,
    CONF_EXCHANGE_RATE_SENSOR_ID,
    CONF_CHARGE,
    OteRateSettings,
)

"""OTE Rate sensor integration."""
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    config = entry.options
    name = config[CONF_NAME]
    currency = config[CONF_CURRENCY]
    charge = config[CONF_CHARGE] if CONF_CHARGE in config else 0
    custom_exchange_rate = (
        config[CONF_EXCHANGE_RATE] if CONF_EXCHANGE_RATE in config else None
    )
    exchange_rate_sensor_id = (
        config[CONF_EXCHANGE_RATE_SENSOR_ID]
        if CONF_EXCHANGE_RATE_SENSOR_ID in config
        else None
    )

    settings = OteRateSettings(
        hass=hass,
        name=name,
        charge=charge,
        custom_exchange_rate=custom_exchange_rate,
        currency=currency,
        exchange_rate_sensor_id=exchange_rate_sensor_id,
    )
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][name] = {
        "settings": settings,
    }

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
