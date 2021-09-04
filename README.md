# OTE Energy Cost Sensor for Home Assistant

This is an integration providing current price per megawatt of energy based on the quote
from ote-cr.cz

### Calculating price in local currency

If you have an exchange rate sensor - you can calculate the value in local currency using template sensor:
```
  - platform: template
    sensors:
      current_electricity_price:
        friendly_name: "Current Electricity Price"
        value_template: >-
          {% set CURRENT_PRICE = states("sensor.current_ote_energy_cost") | float %}
          {% set EUR_CZK = states("sensor.exchange_rate") | float %}
          {{- (CURRENT_PRICE * EUR_CZK / 1000) | round(3) -}}
        unit_of_measurement: "CZK/kWh"
```

### Installation

Copy this folder to `<config_dir>/custom_components/ote_rate/`.
If you're using HACS - feel free to add https://github.com/grinco/ote_rate as custom repository.

Once you've installed the custom integration, add the following to your `configuration.yaml` file:

```yaml
sensor:
  platform: ote_rate
```
