from homeassistant.components.sensor import (
    SensorEntity,
)
from datetime import datetime
import logging

from .const import (
    DOMAIN,
)
from .entity import IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator: OteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([TodayCostsSensor(coordinator, entry)])


class TodayCostsSensor(IntegrationOteEntity, SensorEntity):
    """Sensor for today costs."""

    @property
    def name(self):
        """Return the name of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return f"{coordinator.settings.name} Current Cost"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.today_costs[datetime.now().hour]
