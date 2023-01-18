import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .coordinator import OteDataUpdateCoordinator
from .date_price_sensors import TodayCostsSensor, NextDayCostsSensor
from .lowest_price_sensors import TodayLowestPrice, NextDayLowestPrice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Setup sensor platform."""
    coordinator: OteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TodayCostsSensor(coordinator, entry),
            NextDayCostsSensor(coordinator, entry),
            TodayLowestPrice(coordinator, entry),
            NextDayLowestPrice(coordinator, entry),
        ],
        update_before_add=True,
    )
