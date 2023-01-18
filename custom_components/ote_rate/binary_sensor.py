"""Binary sensors platform for ote rates."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .entity import IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([NextDayAvailableBinarySensor(coordinator, entry)])


class NextDayAvailableBinarySensor(IntegrationOteEntity, BinarySensorEntity):
    """Binary sensor class to signal whether next day prices are available."""

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        return "next_day_available"

    @property
    def _name_post_fix(self):
        """Return the name of the sensor."""
        return "Next Day Available"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.next_day_available
