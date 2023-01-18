from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import OteApiClient
from .state import OteStateData, DatePriceData
from .const import DOMAIN, OTE_DENNI_TRH, DEFAULT_OTE_CURRENCY

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
        energy_unit: str,
    ) -> None:
        """Initialize."""
        self.name = name
        self.currency = currency
        self.charge = charge
        self.custom_exchange_rate = custom_exchange_rate
        self.exchange_rate_sensor_id = exchange_rate_sensor_id
        self.energy_price_unit = f"{currency}/{energy_unit}"


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
            date_costs = self.__prepare_costs(
                await self.api.async_get_costs_for_date(OTE_DENNI_TRH, now)
            )
            next_day_costs = self.__prepare_costs(
                await self.api.async_get_costs_for_date(
                    OTE_DENNI_TRH, now + timedelta(days=1)
                )
            )
            if len(next_day_costs) == 0:
                next_day_costs = None

            state = OteStateData(
                DatePriceData(date_costs),
                DatePriceData(next_day_costs) if next_day_costs is not None else None,
            )
            return state
        except Exception as exception:
            raise UpdateFailed() from exception

    def __prepare_costs(self, costs: dict) -> dict:
        return self.__apply_charges(self.__convert_to_currency(costs))

    def __convert_to_currency(self, costs: dict) -> dict:
        price = self.settings.currency
        if self.settings.currency == DEFAULT_OTE_CURRENCY:
            return costs

        converted = dict()

        sensor_rate_state = self.hass.states.get(self.settings.exchange_rate_sensor_id)

        exchange_rate = (
            float(sensor_rate_state.state)
            if sensor_rate_state is not None and sensor_rate_state.state != "unknown"
            else self.settings.custom_exchange_rate
        )

        for hour, price in costs.items():
            converted[hour] = price * exchange_rate

        return converted

    def __apply_charges(self, costs: dict) -> dict:
        charge = self.settings.charge
        if charge == 0:
            return costs

        converted = dict()

        for hour, price in costs.items():
            converted[hour] = price - charge

        return converted
