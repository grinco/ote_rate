"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity

""" External Imports """
import requests
import json
import datetime

""" Constants """
UNIT_OF_MEASUREMENT = "EUR/mWh"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([OTERateSensor()])


class OTERateSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Current OTE Energy Cost'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UNIT_OF_MEASUREMENT

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.get_current_value()

    def get_current_value():
        """ Parse the data and return value in EUR/kWh
        """

        eur_kwh = 0
        cost_data = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"
        # todo: add secondary validations
        cost_table = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh"
        cost_table2 = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/multi-regional-coupling"

        date = datetime.datetime.now()
        params = dict (
            date = date.strftime('%Y-%m-%d')
        )

        response = requests.get(url=cost_data, params=params)
        json_data = response.json()

        return eur_kwh
