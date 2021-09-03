"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity

""" External Imports """
import requests
import json
import datetime
import logging


""" Constants """
UNIT_OF_MEASUREMENT = "EUR/mWh"
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([OTERateSensor()], update_before_add=True)


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

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._get_current_value()

    def _get_current_value(self):
        """ Parse the data and return value in EUR/kWh
        """

        try:
          eur_mwh = 0
          cost_string = "Cena (EUR/MWh)"
          cost_data = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"
          # todo: add secondary validations
          cost_table = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh"
          cost_table2 = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/multi-regional-coupling"

          date = datetime.datetime.now()
          params = dict (
              date = date.strftime('%Y-%m-%d')
          )

          response = requests.get(url=cost_data, params=params)
          json = response.json()
          axis = ""
          for key in json['axis'].keys():
              if json['axis'][key]['legend'] == cost_string:
                  axis = key

          for values in json['data']['dataLine']:
              if values['title'] == cost_string:
                  eur_mwh = values['point'][date.hour][axis]

          self._state = float(eur_mwh)
          self._available = True
        except:
          self._available = False
          _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")