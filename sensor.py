from homeassistant.components.sensor import (
    SensorEntity,
)
import aiohttp
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging
from .const import (
    NEXT_DAY_AVAILABLE_ATTRIBUTE,
    NEXT_DAY_PREFIX,
    DEVICE_CLASS,
    NATIVE_UNIT_OF_MEASUREMENT,
    HOUR_RESPONSE_NAME,
    COST_RESPONSE_NAME,
    OTE_URL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Set up the sensor platform."""
    async_add_entities([OTERateSensor(hass)], update_before_add=True)


class OTERateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._value = None
        self._attr = None
        self._hass = hass

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Current OTE Energy Cost"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return NATIVE_UNIT_OF_MEASUREMENT

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attr

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self) -> None:
        """Parse the data from OTE"""
        try:

            now = datetime.now()
            next_day = datetime.now() + timedelta(days=1)

            today_costs: DateCosts = await self.__async_get_costs_for_date(now)
            next_day_costs: DateCosts = await self.__async_get_costs_for_date(next_day)

            attributes = dict()

            for hour, cost in today_costs.cost_history.items():
                attributes[hour] = cost

            for hour, cost in next_day_costs.cost_history.items():
                attributes[f"{NEXT_DAY_PREFIX}{hour}"] = cost

            attributes[NEXT_DAY_AVAILABLE_ATTRIBUTE] = (
                len(next_day_costs.cost_history) > 0
            )

            self._value = today_costs.date_cost
            self._attr = attributes
            self._available = True
        except:
            self._available = False
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz")

    async def __async_get_costs_for_date(self, date: datetime) -> "DateCosts":
        params = {"report_date": date.strftime("%Y-%m-%d")}

        async with aiohttp.ClientSession() as session:
            async with session.get(OTE_URL, params=params) as resp:
                return self.__parse_response_with_costs(date, await resp.json())

    def __parse_response_with_costs(self, date: datetime, json) -> "DateCosts":
        cost_history = dict()
        cost_axis = ""
        hour_axis = ""
        current_cost = 0
        history_index = 0

        for key in json["axis"].keys():
            if json["axis"][key]["legend"] == COST_RESPONSE_NAME:
                cost_axis = key
            if json["axis"][key]["legend"] == HOUR_RESPONSE_NAME:
                hour_axis = key

        for values in json["data"]["dataLine"]:
            if values["title"] == COST_RESPONSE_NAME:
                for data in values["point"]:
                    history_index = int(data[hour_axis]) - 1
                    cost_history[history_index] = float(data[cost_axis])
                current_cost = cost_history[date.hour]

        return DateCosts(cost_history, current_cost)


class DateCosts:
    def __init__(self, cost_history: dict, date_cost: float) -> None:
        self.cost_history = cost_history
        self.date_cost = date_cost
