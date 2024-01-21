[![Push actions](https://github.com/grinco/ote_rate/actions/workflows/push.yml/badge.svg)](https://github.com/grinco/ote_rate/actions/workflows/push.yml)
[![Build actions](https://github.com/grinco/ote_rate/actions/workflows/build.yaml/badge.svg)](https://github.com/grinco/ote_rate/actions/workflows/build.yaml)

# OTE Energy Cost Sensor for Home Assistant

This is an integration providing current price per megawatt of energy based on the quote
from ote-cr.cz

### Installation

Copy this folder to `<config_dir>/custom_components/ote_rate/`.

If you're using HACS - feel free to add https://github.com/grinco/ote_rate as custom repository.

Once you've installed the custom integration, add this integration through the integration setup UI.

### Calculating price in a local currency
You can calculate price in a local currency, either using custom value or exchange rate sensor (follow setup flow).

### Adding costs to price
For example if you sell energy and your provider has some fee, you can set costs which will be deducted from OTE price.
