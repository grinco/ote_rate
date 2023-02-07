"""Binary sensors platform for ote rates."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .entity import BaseOteSensorEntityDescription, IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for sensor in sensors:
        entities.append(
            BaseOteBinarySensorEntity(
                coordinator=coordinator, entity_description=sensor, config_entry=entry
            )
        )

    async_add_devices(entities)


sensors = [
    BaseOteSensorEntityDescription(
        key="next_day_available",
        name="Next Day Available",
        state_getter=lambda s: s.next_day_available,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )
]


class BaseOteBinarySensorEntity(IntegrationOteEntity, BinarySensorEntity):
    """Base class for all binary sensor entities."""

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        if hasattr(self.entity_description, "state_getter"):
            return self.entity_description.state_getter(coordinator.data)

        return None

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        if hasattr(self.entity_description, "state_getter"):
            return self.entity_description.state_getter(coordinator.data)

        return None
