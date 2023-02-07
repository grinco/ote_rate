from dataclasses import dataclass


@dataclass
class DatePriceData:
    """Class for keeping track of date prices."""

    def __init__(self, hour_prices: dict[int, float]) -> None:
        """Initialize."""
        self.hour_prices = hour_prices

        self.lowest_price_hour = min(hour_prices, key=hour_prices.get)
        self.lowest_price = hour_prices[self.lowest_price_hour]

        self.highest_price_hour = max(hour_prices, key=hour_prices.get)
        self.highest_price = hour_prices[self.highest_price_hour]
        self.attributes = {
            "hour_prices": hour_prices,
            "lowest_price_hour": min(hour_prices, key=hour_prices.get),
            "lowest_price": hour_prices[self.lowest_price_hour],
            "highest_price_hour": max(hour_prices, key=hour_prices.get),
            "highest_price": hour_prices[self.highest_price_hour],
        }


@dataclass
class OteStateData:
    """Class for keeping track of ote states."""

    today_costs: DatePriceData
    next_day_costs: DatePriceData | None

    @property
    def next_day_available(self) -> bool:
        """Are next day prices available?."""
        return self.next_day_costs is not None
