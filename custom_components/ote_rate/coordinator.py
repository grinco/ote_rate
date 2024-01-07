from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import OteApiClient
from .state import OteStateData, DatePriceData
from .const import *

SCAN_INTERVAL = timedelta(minutes=1)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class OteRateSettings:
    """Class to manage component settings."""

    def __init__(
        self,
        name: str,
        currency: str,
        charge: float,
        custom_exchange_rate: float,
        exchange_rate_sensor_id: str | None,
        energy_unit: str,
        number_of_digits: int,
        add_distribution_fees: bool,
        distribution_fee_h: float | None,
        distribution_fee_l: float | None,
        tax_fee: float | None,
        system_services_fee: float | None,
        ote_fee: float | None,
        poze_fee: float | None,
        tax: float | None,
        distribution_lower_prices_hours: dict[str, list[int]] | None,
    ) -> None:
        """Initialize."""
        self.name = name
        self.currency = currency
        self.charge = charge
        self.custom_exchange_rate = custom_exchange_rate
        self.exchange_rate_sensor_id = exchange_rate_sensor_id
        self.energy_price_unit = f"{currency}/{energy_unit}"
        self.number_of_digits = number_of_digits
        self.add_distribution_fees = add_distribution_fees
        self.distribution_fee_h = distribution_fee_h
        self.distribution_fee_l = distribution_fee_l
        self.tax_fee = tax_fee
        self.system_services_fee = system_services_fee
        self.ote_fee = ote_fee
        self.poze_fee = poze_fee
        self.tax = tax
        self.distribution_lower_prices_hours = distribution_lower_prices_hours


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
                await self.api.async_get_costs_for_date(OTE_DENNI_TRH, now),
                now.weekday(),
            )

            if len(date_costs) == 0:
                return self.data

            next_day = now + timedelta(days=1)
            next_day_costs = self.__prepare_costs(
                await self.api.async_get_costs_for_date(OTE_DENNI_TRH, next_day),
                next_day.weekday(),
            )
            if len(next_day_costs) == 0:
                next_day_costs = None

            state = OteStateData(
                DatePriceData(date_costs),
                DatePriceData(next_day_costs) if next_day_costs is not None else None,
            )

            if self.settings.add_distribution_fees is True:
                self.__add_fees_atrributes(state.today_costs)
                if state.next_day_costs is not None:
                    self.__add_fees_atrributes(state.next_day_costs)

            return state
        except Exception as exception:
            _LOGGER.error("Error fetching data: " + str(exception))
            return self.data

    def __add_fees_atrributes(self, date_price_data: DatePriceData) -> None:
        date_price_data.attributes["ote_fee"] = self.settings.ote_fee
        date_price_data.attributes["poze_fee"] = self.settings.poze_fee
        date_price_data.attributes[
            "system_services_fee"
        ] = self.settings.system_services_fee
        date_price_data.attributes["tax_fee"] = self.settings.tax_fee
        date_price_data.attributes[
            "distribution_fee_h"
        ] = self.settings.distribution_fee_h
        date_price_data.attributes[
            "distribution_fee_l"
        ] = self.settings.distribution_fee_l
        date_price_data.attributes["tax"] = self.settings.tax
        date_price_data.attributes[
            "lower_price_hours"
        ] = self.settings.distribution_lower_prices_hours
        date_price_data.attributes["total_fees_low_including_tax"] = (
            self.settings.ote_fee
            + self.settings.poze_fee
            + self.settings.system_services_fee
            + self.settings.tax_fee
            + self.settings.distribution_fee_l
        ) * (1 + self.settings.tax / 100)
        date_price_data.attributes["total_fees_high_including_tax"] = (
            self.settings.ote_fee
            + self.settings.poze_fee
            + self.settings.system_services_fee
            + self.settings.tax_fee
            + self.settings.distribution_fee_h
        ) * (1 + self.settings.tax / 100)

    def __prepare_costs(self, costs: dict, weekday: int) -> dict:
        return self.__round(
            self.__apply_charges(self.__convert_to_currency(costs), weekday)
        )

    def __convert_to_currency(self, costs: dict) -> dict:
        price = self.settings.currency
        if self.settings.currency == DEFAULT_OTE_CURRENCY:
            return costs

        converted = dict()

        sensor_rate_state = (
            self.hass.states.get(self.settings.exchange_rate_sensor_id)
            if self.settings.exchange_rate_sensor_id is not None
            else None
        )

        exchange_rate = (
            float(sensor_rate_state.state)
            if sensor_rate_state is not None and sensor_rate_state.state != "unknown"
            else self.settings.custom_exchange_rate
        )

        for hour, price in costs.items():
            converted[hour] = price * exchange_rate

        return converted

    def __apply_charges(self, costs: dict, weekday: int) -> dict:
        charge = self.settings.charge
        if charge == 0 and self.settings.add_distribution_fees is False:
            return costs

        converted = dict()

        for hour, price in costs.items():
            converted[hour] = price - charge
            if self.settings.add_distribution_fees is True:
                lower_prices_hours = self.settings.distribution_lower_prices_hours[
                    DAYS[weekday]
                ]

                converted[hour] += (
                    self.settings.ote_fee
                    + self.settings.poze_fee
                    + self.settings.system_services_fee
                    + self.settings.tax_fee
                )
                converted[hour] += (
                    self.settings.distribution_fee_l
                    if hour in lower_prices_hours
                    else self.settings.distribution_fee_h
                )
                converted[hour] *= 1 + self.settings.tax / 100

        return converted

    def __round(self, costs: dict) -> dict:
        converted = dict()

        for hour, price in costs.items():
            converted[hour] = round(price, self.settings.number_of_digits)

        return converted
