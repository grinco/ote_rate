"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    SensorEntity,
    SensorEntityDescription,
)

""" External Imports """
import requests
import json
import datetime
import logging


""" Constants """
NATIVE_UNIT_OF_MEASUREMENT = "EUR/MWh"
DEVICE_CLASS = "monetary"

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([OTERateSensor()], update_before_add=True)


class OTERateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._value = None
        self._attr = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Current OTE Energy Cost'

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return NATIVE_UNIT_OF_MEASUREMENT

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attr

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
          current_cost = 0
          cost_history = dict()
          history_index = 0
          cost_string = "Cena (EUR/MWh)"
          hour_string = "Hodina"
          cost_data = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"

          date = datetime.datetime.now()
          params = dict (
              date = date.strftime('%Y-%m-%d')
          )

          response = requests.get(url=cost_data, params=params)
          json = response.json()
          cost_axis = ""
          hour_axis = ""
          for key in json['axis'].keys():
              if json['axis'][key]['legend'] == cost_string:
                  cost_axis = key
              if json['axis'][key]['legend'] == hour_string:
                  hour_axis = key


          for values in json['data']['dataLine']:
              if values['title'] == cost_string:
                  for data in values['point']:
                     history_index = int(data[hour_axis])-1
                     cost_history[history_index] = float(data[cost_axis])
                  current_cost = cost_history[date.hour]


          self._value = current_cost
          self._attr = cost_history
          self._available = True
        except:
          self._available = False
          _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
