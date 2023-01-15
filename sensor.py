from homeassistant.components.sensor import (
    SensorEntity,
)
import requests
from datetime import datetime, timedelta
import logging
from .const import (
    NEXT_DAY_AVAILABLE_ATTRIBUTE,
    NEXT_DAY_PREFIX,
    DEVICE_CLASS,
    NATIVE_UNIT_OF_MEASUREMENT,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None) -> None:
    """Set up the sensor platform."""
    add_entities([OTERateSensor(hass)], update_before_add=True)


class OTERateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass) -> None:
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

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._get_current_value()

    def _get_current_value(self) -> None:
        """Parse the data and return value in EUR/kWh"""

        try:

            now = datetime.now()
            next_day = datetime.now() + timedelta(days=1)

            today_costs: DateCosts = self._get_costs_for_date(now)
            next_day_costs: DateCosts = self._get_costs_for_date(next_day)

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

    def _get_costs_for_date(self, date: datetime) -> "DateCosts":
        current_cost = 0
        cost_history = dict()
        history_index = 0
        cost_string = "Cena (EUR/MWh)"
        hour_string = "Hodina"
        cost_data = (
            "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"
        )

        params = dict(date=date.strftime("%Y-%m-%d"))

        response = requests.get(url=cost_data, params=params, timeout=60)

        json = response.json()

        cost_axis = ""
        hour_axis = ""
        for key in json["axis"].keys():
            if json["axis"][key]["legend"] == cost_string:
                cost_axis = key
            if json["axis"][key]["legend"] == hour_string:
                hour_axis = key

        for values in json["data"]["dataLine"]:
            if values["title"] == cost_string:
                for data in values["point"]:
                    history_index = int(data[hour_axis]) - 1
                    cost_history[history_index] = float(data[cost_axis])
                current_cost = cost_history[date.hour]

        return DateCosts(cost_history, current_cost)


class DateCosts:
    def __init__(self, cost_history: dict, date_cost: float) -> None:
        self.cost_history = cost_history
        self.date_cost = date_cost
