"""OteEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, ATTR_MANUFACTURER, VERSION, ATTRIBUTION
from .coordinator import OteDataUpdateCoordinator


class IntegrationOteEntity(CoordinatorEntity):
    """A class for entities using DataUpdateCoordinator."""

    def __init__(
        self, coordinator: OteDataUpdateCoordinator, config_entry: ConfigEntry
    ):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return DeviceInfo(
            name=coordinator.settings.name,
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer=ATTR_MANUFACTURER,
            model=VERSION,
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            # "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
