# Example Sensor

This is an integration providing current price per megawatt of energy based on the quote
from ote-cr.cz

### Alternative
Same can be achieved through the follwoing configuration:
```
  - platform: rest
    resource_template: https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data?date{{ now().strftime('%Y-%m-%d') }}
    value_template: "{{ value_json.data.dataLine[1].point[now().hour].y | round(2)}}"
    unit_of_measurement: 'EUR/mWh'
    name: "Current Energy cost in EUR/mWh"
```

If you have an exchange rate sensor - you can calculate the value using template sensor:
```
  - platform: template
    sensors:
      current_electricity_price:
        friendly_name: "Current Electricity Price"
        value_template: >-
          {% set CURRENT_PRICE = states("sensor.current_energy_cost_in_eur_mwh") | float %}
          {% set EUR_CZK = states("sensor.exchange_rate") | float %}
          {{- (CURRENT_PRICE * EUR_CZK / 1000) | round(3) -}}
        unit_of_measurement: "CZK/kWh"
```

### Installation

Copy this folder to `<config_dir>/custom_components/ote_rate/`.

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  platform: ote_rate
```
