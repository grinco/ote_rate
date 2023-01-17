import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import OteApiClient
from .state import OteStateData
from datetime import datetime, timedelta
from .const import DOMAIN, OTE_DENNI_TRH

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class OteRateSettings:
    """Class to manage component settings."""

    def __init__(
        self,
        name: str,
        currency: str,
        charge: float,
        custom_exchange_rate: float,
        exchange_rate_sensor_id: str,
    ) -> None:
        """Initialize."""
        self.name = name
        self.currency = currency
        self.charge = charge
        self.custom_exchange_rate = custom_exchange_rate
        self.exchange_rate_sensor_id = exchange_rate_sensor_id


class OteDataUpdateCoordinator(DataUpdateCoordinator[OteStateData]):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: OteApiClient, settings: OteRateSettings
    ) -> None:
        """Initialize."""
        self.api = client
        self.settings = settings
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self) -> OteStateData:
        """Update data via library."""
        try:
            now = datetime.now()
            date_costs = await self.api.async_get_costs_for_date(OTE_DENNI_TRH, now)
            next_day_costs = await self.api.async_get_costs_for_date(
                OTE_DENNI_TRH, now + timedelta(days=1)
            )
            if len(next_day_costs) == 0:
                next_day_costs = None

            state = OteStateData(date_costs, next_day_costs)
            return state
        except Exception as exception:
            raise UpdateFailed() from exception
