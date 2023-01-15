from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.helpers.entity import DeviceInfo
import aiohttp
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
import logging
from typing import Optional

from .const import (
    HOUR_RESPONSE_NAME,
    COST_RESPONSE_NAME,
    OTE_URL,
    DOMAIN,
    ATTR_MANUFACTURER,
    OteRateSettings,
    MWH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Set up the sensor platform."""
    name = config.options[CONF_NAME]
    settings: OteRateSettings = hass.data[DOMAIN][name]["settings"]
    device_info = DeviceInfo(
        name=name, identifiers={(DOMAIN, name)}, manufacturer=ATTR_MANUFACTURER
    )

    today_sensor_description = SensorEntityDescription(
        key="current_cost",
        name=f"{settings.name} Current Cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=f"{settings.currency}/{MWH}",
    )
    today_sensor = OTERateSensor(
        hass, settings, device_info, today_sensor_description, timedelta()
    )

    next_day_sensor_description = SensorEntityDescription(
        key="next_day_cost",
        name=f"{settings.name} Next Day",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=f"{settings.currency}/{MWH}",
    )
    next_day_sensor = OTERateSensor(
        hass, settings, device_info, next_day_sensor_description, timedelta(days=1)
    )

    async_add_entities([today_sensor, next_day_sensor], update_before_add=True)


class OTERateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        settings: OteRateSettings,
        device_info: DeviceInfo,
        description: SensorEntityDescription,
        timedelta: timedelta,
    ) -> None:
        """Initialize the sensor."""
        self._value = None
        self._attr = None
        self._platform_name = "OTE Energy"
        self._hass = hass
        self._settings = settings
        self._attr_device_info = device_info
        self.entity_description = description
        self._timedelta = timedelta

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attr

    @property
    def unique_id(self) -> Optional[str]:
        print(f"{self._platform_name}_{self.entity_description.key}")
        return f"{self._platform_name}_{self.entity_description.key}"

    async def async_update(self) -> None:
        """Parse the data from OTE"""
        try:

            date = datetime.now() + self._timedelta
            date_costs = await self.__async_get_costs_for_date(date)

            attributes = dict()

            for hour, cost in date_costs.items():
                attributes[hour] = cost

            self._attr_available = len(date_costs) > 0
            if self._attr_available:
                self._value = date_costs[date.hour]
            else:
                self._value = None

            self._attr = attributes
        except:
            self._attr_available = False
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz")

    async def __async_get_costs_for_date(self, date: datetime) -> dict:
        params = {"report_date": date.strftime("%Y-%m-%d")}

        async with aiohttp.ClientSession() as session:
            async with session.get(OTE_URL, params=params) as resp:
                return self.__parse_response_with_costs(date, await resp.json())

    def __parse_response_with_costs(self, date: datetime, json) -> dict:
        date_costs = dict()
        cost_axis = ""
        hour_axis = ""
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
                    date_costs[history_index] = float(data[cost_axis])

        return date_costs
