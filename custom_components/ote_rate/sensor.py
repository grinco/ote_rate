import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .entity import BaseOteSensorEntityDescription, IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator
from datetime import datetime
from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)


_LOGGER = logging.getLogger(__name__)


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
        extra_attributes_getter=lambda s: s.next_day_costs.attributes,
        state_getter=lambda s: s.next_day_costs.hour_prices[datetime.now().hour]
        if hasattr(s, "next_day_costs")
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
