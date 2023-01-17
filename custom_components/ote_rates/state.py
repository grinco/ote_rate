from dataclasses import dataclass

@dataclass
class OteStateData:
    """Class for keeping track of ote states."""
    today_costs: dict
    next_day_costs: dict | None

    def next_day_available(self) -> bool:
        return self.next_day_costs is not None