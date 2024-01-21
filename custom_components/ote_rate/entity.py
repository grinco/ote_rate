"""OteEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from .state import OteStateData
from homeassistant.components.sensor import (
    SensorEntityDescription,
)
from dataclasses import dataclass
from typing import Any, Callable, Mapping, TypeVar
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)


from .const import DOMAIN, ATTR_MANUFACTURER, VERSION, ATTRIBUTION
from .coordinator import OteDataUpdateCoordinator

T = TypeVar("T")


@dataclass
class BaseOteSensorEntityDescription(SensorEntityDescription):
    """base class for ote sensor declarations"""

    extra_attributes_getter: Callable[[OteStateData], T] | None = None
    state_getter: Callable[[OteStateData], T] = None
    unit_of_measurement_getter: Callable[[OteDataUpdateCoordinator], str] | None = None


class IntegrationOteEntity(CoordinatorEntity):
    """A class for entities using DataUpdateCoordinator."""

    _attr_attribution = ATTRIBUTION
    entity_description: BaseOteSensorEntityDescription

    def __init__(
        self,
        coordinator: OteDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: BaseOteSensorEntityDescription,
    ):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = entity_description
        self._attr_unit_of_measurement = (
            entity_description.unit_of_measurement_getter(coordinator)
            if callable(entity_description.unit_of_measurement_getter)
            else None
        )

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name}_{self.entity_description.key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name} {self.entity_description.name}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name}_{self.config_entry.entry_id}_{self.entity_description.key}"

    @property
    def device_info(self):
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return DeviceInfo(
            name=coordinator.settings.name,
            identifiers={(DOMAIN, coordinator.settings.name)},
            manufacturer=ATTR_MANUFACTURER,
            model=VERSION,
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
            "id": self.key,
            "integration": DOMAIN,
        }
        coordinator: OteDataUpdateCoordinator = self.coordinator

        if callable(self.entity_description.extra_attributes_getter):
            attributes = attributes | self.entity_description.extra_attributes_getter(
                coordinator.data
            )

        # if (
        #     "extra_attributes_data" in self.entity_description
        #     and self.entity_description.extra_attributes_data is not None
        # ):
        #     attributes = attributes | self.entity_description.extra_attributes_data

        return attributes
