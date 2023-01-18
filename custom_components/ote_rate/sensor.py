from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorEntityDescription,
)
from datetime import datetime
import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from abc import abstractmethod
from .const import DOMAIN, MWH
from .entity import IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Setup sensor platform."""
    coordinator: OteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [TodayCostsSensor(coordinator, entry), NextDayCostsSensor(coordinator, entry)],
        update_before_add=True,
    )


class CostsSensor(IntegrationOteEntity, SensorEntity):
    """Sensor for costs."""

    def __init__(
        self, coordinator: OteDataUpdateCoordinator, config_entry: ConfigEntry
    ):
        super().__init__(coordinator, config_entry)
        self.entity_description = SensorEntityDescription(
            device_class=SensorDeviceClass.MONETARY,
            native_unit_of_measurement=f"{coordinator.settings.currency}/{MWH}",
            key=self.key,
        )

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        return ""

    @abstractmethod
    def get_costs(self) -> dict:
        """Implement to return costs for current sensor"""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        costs = self.get_costs()
        return costs[datetime.now().hour] if costs is not None else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = super(CostsSensor, self).extra_state_attributes
        costs = self.get_costs()
        if costs is not None:
            attributes = attributes | costs

        return attributes


class TodayCostsSensor(CostsSensor):
    """Sensor for today costs."""

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        return "today_costs"

    @property
    def name(self):
        """Return the name of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name} Current Cost"

    def get_costs(self) -> dict:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.today_costs


class NextDayCostsSensor(CostsSensor):
    """Sensor for next day costs."""

    @property
    def key(self):
        """Return a unique key to use for this entity."""
        return "next_day_costs"

    @property
    def name(self):
        """Return the name of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name} Next Day Cost"

    def get_costs(self) -> dict:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.next_day_costs
