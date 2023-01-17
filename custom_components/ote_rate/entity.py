"""OteEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, ATTR_MANUFACTURER, VERSION, ATTRIBUTION
from .coordinator import OteDataUpdateCoordinator


class IntegrationOteEntity(CoordinatorEntity):
    """A class for entities using DataUpdateCoordinator."""
    _attr_attribution = ATTRIBUTION
    _attr_attribution = ATTRIBUTION
    def __init__(
        self, coordinator: OteDataUpdateCoordinator, config_entry: ConfigEntry
    ):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        return ""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        print(f"{coordinator.settings.name}_{self.config_entry.entry_id}_{self.key}")
        return f"{coordinator.settings.name}_{self.config_entry.entry_id}_{self.key}"

    @property
    def device_info(self):
        coordinator: OteDataUpdateCoordinator = self.coordinator
        print((DOMAIN, coordinator.settings.name))
        return DeviceInfo(
            name=coordinator.settings.name,
            identifiers={(DOMAIN, coordinator.settings.name)},
            manufacturer=ATTR_MANUFACTURER,
            model=VERSION,
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "id": self.key,
            "integration": DOMAIN,
        }
