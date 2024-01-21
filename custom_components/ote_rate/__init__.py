import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import *
from .coordinator import OteDataUpdateCoordinator, OteRateSettings
from .api import OteApiClient

"""OTE Rate sensor integration."""
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Activate the legacy ote rate sensor."""
    if DOMAIN not in config:
        return True

    config = config[DOMAIN]
    hass.config_entries.async_setup()

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info("OTE rates setup started")

    currency = config_entry.options[CONF_CURRENCY]

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
        currency=currency,
        exchange_rate_sensor_id=(
            config_entry.options[CONF_EXCHANGE_RATE_SENSOR_ID]
            if CONF_EXCHANGE_RATE_SENSOR_ID in config_entry.options
            else None
        ),
        energy_unit=MWH,
        number_of_digits=0 if currency == CURRENCY_CZK else 2,
        add_distribution_fees=config_entry.options[CONF_ADD_DISTRIBUTION_FEES]
        if CONF_ADD_DISTRIBUTION_FEES in config_entry.options
        else False,
        distribution_fee_h=config_entry.options[CONF_DISTRIBUTION_FEE_H]
        if CONF_DISTRIBUTION_FEE_H in config_entry.options
        else None,
        distribution_fee_l=config_entry.options[CONF_DISTRIBUTION_FEE_L]
        if CONF_DISTRIBUTION_FEE_L in config_entry.options
        else None,
        tax_fee=config_entry.options[CONF_TAX_FEE]
        if CONF_TAX_FEE in config_entry.options
        else None,
        system_services_fee=config_entry.options[CONF_SYSTEM_SERVICES_FEE]
        if CONF_SYSTEM_SERVICES_FEE in config_entry.options
        else None,
        ote_fee=config_entry.options[CONF_OTE_FEE]
        if CONF_OTE_FEE in config_entry.options
        else None,
        poze_fee=config_entry.options[CONF_POZE_FEE]
        if CONF_POZE_FEE in config_entry.options
        else None,
        tax=config_entry.options[CONF_TAX]
        if CONF_TAX in config_entry.options
        else None,
        distribution_lower_prices_hours=config_entry.options[
            CONF_DISTRIBUTION_LOWER_PRICES_HOURS
        ]
        if CONF_DISTRIBUTION_LOWER_PRICES_HOURS in config_entry.options
        else None,
    )

    session = async_get_clientsession(hass)
    client = OteApiClient(session)
    coordinator = OteDataUpdateCoordinator(hass, client=client, settings=settings)
    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
