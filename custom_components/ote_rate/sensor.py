import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, OTE_DENNI_TRH
from .entity import BaseOteSensorEntityDescription, IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator
from .api import OteApiClient
from datetime import datetime
from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.warn(
        "OTE Legacy sensor is deprecated and will be removed in the future. Please use config flow to setup OTE rates sensors instead."
    )

    session = async_get_clientsession(hass)
    client = OteApiClient(session)

    add_entities([LegacyOTERateSensor(client)], update_before_add=True)


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Setup sensor platform."""
    coordinator: OteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for sensor in sensors:
        entities.append(
            BaseOteSensorEntity(
                coordinator=coordinator, entity_description=sensor, config_entry=entry
            )
        )

    async_add_entities(entities, update_before_add=True)


sensors = [
    BaseOteSensorEntityDescription(
        key="today_costs",
        name="Current Cost",
        extra_attributes_getter=lambda s: s.today_costs.attributes,
        state_getter=lambda s: s.today_costs.hour_prices[datetime.now().hour],
        unit_of_measurement_getter=lambda coordinator: coordinator.settings.energy_price_unit,
        device_class=SensorDeviceClass.MONETARY,
    ),
    BaseOteSensorEntityDescription(
        key="next_day_costs",
        name="Next Day Cost",
        extra_attributes_getter=lambda s: s.next_day_costs.attributes
        if s.next_day_costs is not None
        else {},
        state_getter=lambda s: s.next_day_costs.hour_prices[datetime.now().hour]
        if s.next_day_costs is not None
        else None,
        unit_of_measurement_getter=lambda coordinator: coordinator.settings.energy_price_unit,
        device_class=SensorDeviceClass.MONETARY,
    ),
]


class BaseOteSensorEntity(IntegrationOteEntity, SensorEntity):
    """Base class for all sensor entities."""

    def __init__(
        self,
        coordinator: OteDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: BaseOteSensorEntityDescription,
    ):
        super().__init__(coordinator, config_entry, entity_description)
        self._attr_native_unit_of_measurement = (
            entity_description.unit_of_measurement_getter(coordinator)
            if callable(entity_description.unit_of_measurement_getter)
            else None
        )

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        if callable(self.entity_description.state_getter):
            return self.entity_description.state_getter(coordinator.data)

        return None


class LegacyOTERateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, client: OteApiClient):
        """Initialize the sensor."""
        self._value = None
        self._attr = None
        self._client = client

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
        return "EUR/MWh"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "monetary"

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attr

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """

        try:
            date = datetime.now()
            cost_history = await self._client.async_get_costs_for_date(
                OTE_DENNI_TRH, date
            )
            self._value = cost_history[date.hour]
            self._attr = cost_history
            self._available = True
        except:
            self._available = False
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
