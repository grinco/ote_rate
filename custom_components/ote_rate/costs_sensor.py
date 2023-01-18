from abc import abstractmethod
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from .entity import IntegrationOteEntity
from .coordinator import OteDataUpdateCoordinator
from .state import DatePriceData


class CostsSensor(IntegrationOteEntity, SensorEntity):
    """Sensor for costs."""

    def __init__(
        self, coordinator: OteDataUpdateCoordinator, config_entry: ConfigEntry
    ):
        super().__init__(coordinator, config_entry)
        self.entity_description = SensorEntityDescription(
            device_class=SensorDeviceClass.MONETARY,
            native_unit_of_measurement=coordinator.settings.energy_price_unit,
            key=self.key,
        )

    @abstractmethod
    def _get_price_data(self) -> DatePriceData | None:
        """Implement to return costs for current sensor"""
