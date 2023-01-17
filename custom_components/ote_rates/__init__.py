from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
from .const import (
    CONF_CURRENCY,
    DOMAIN,
    CONF_EXCHANGE_RATE,
    CONF_EXCHANGE_RATE_SENSOR_ID,
    CONF_CHARGE,
)
from .coordinator import OteDataUpdateCoordinator, OteRateSettings
from .api import OteApiClient

"""OTE Rate sensor integration."""
PLATFORMS = [Platform.SENSOR]
_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info("OTE rates setup started")

    settings = OteRateSettings(
        name=config_entry.options[CONF_NAME],
        charge=config_entry.options[CONF_CHARGE]
        if CONF_CHARGE in config_entry.options
        else 0,
        custom_exchange_rate=(
            config_entry.options[CONF_EXCHANGE_RATE]
            if CONF_EXCHANGE_RATE in config_entry.options
            else None
        ),
        currency=config_entry.options[CONF_CURRENCY],
        exchange_rate_sensor_id=(
            config_entry.options[CONF_EXCHANGE_RATE_SENSOR_ID]
            if CONF_EXCHANGE_RATE_SENSOR_ID in config_entry.options
            else None
        ),
    )

    session = async_get_clientsession(hass)
    client = OteApiClient(session)
    coordinator = OteDataUpdateCoordinator(hass, client=client, settings=settings)
    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True
