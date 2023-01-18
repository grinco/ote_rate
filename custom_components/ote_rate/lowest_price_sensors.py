from .costs_sensor import CostsSensor
from .coordinator import OteDataUpdateCoordinator
from .state import DatePriceData


class LowestPriceSensor(CostsSensor):
    """Sensor for lower price of a day."""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        costs = self._get_price_data()
        return costs.lowest_price if costs is not None else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        costs = self._get_price_data()
        attributes = {"hour": costs.lowest_price_hour} if costs is not None else dict()
        attributes = attributes | super(LowestPriceSensor, self).extra_state_attributes
        return attributes


class TodayLowestPrice(LowestPriceSensor):
    """Sensor for lower price of a day."""

    key = "today_lowest_price"
    _name_post_fix = "Today Lowest Price"

    def _get_price_data(self) -> DatePriceData | None:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.today_costs


class NextDayLowestPrice(LowestPriceSensor):
    """Sensor for lower price of the next day."""

    key = "next_day_lowest_price"
    _name_post_fix = "Next Day Lowest Price"

    def _get_price_data(self) -> DatePriceData | None:
        coordinator: OteDataUpdateCoordinator = self.coordinator
        return coordinator.data.next_day_costs
