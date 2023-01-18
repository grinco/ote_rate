from datetime import datetime
from .coordinator import OteDataUpdateCoordinator
from .state import DatePriceData
from .costs_sensor import CostsSensor


class DatePriceSensor(CostsSensor):
    """Sensor for costs."""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        costs = self._get_price_data()
        return costs.hour_prices[datetime.now().hour] if costs is not None else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = super(DatePriceSensor, self).extra_state_attributes
        costs = self._get_price_data()
        if costs is not None:
            attributes = attributes | costs.hour_prices

        return attributes


class TodayCostsSensor(DatePriceSensor):
    """Sensor for today costs."""

    key = "today_costs"
    _name_post_fix = "Current Cost"

    def _get_price_data(self) -> DatePriceData | None:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.today_costs


class NextDayCostsSensor(DatePriceSensor):
    """Sensor for next day costs."""

    key = "next_day_costs"
    _name_post_fix = "Next Day Cost"

    def _get_price_data(self) -> DatePriceData | None:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.next_day_costs
