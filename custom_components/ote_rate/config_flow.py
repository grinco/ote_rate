from collections.abc import Mapping
from typing import Any, cast
import logging
import array as arr

import voluptuous as vol
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from .const import *

_LOGGER: logging.Logger = logging.getLogger(__package__)

CURRENCIES = [
    selector.SelectOptionDict(value=CURRENCY_EUR, label=CURRENCY_EUR),
    selector.SelectOptionDict(value=CURRENCY_CZK, label=CURRENCY_CZK),
]

COMMON_SCHEMA = {
    vol.Optional(CONF_CHARGE, default=0): selector.NumberSelector(
        selector.NumberSelectorConfig(step=0.01, mode=selector.NumberSelectorMode.BOX)
    ),
    vol.Required(CONF_CURRENCY, default=CURRENCY_EUR): selector.SelectSelector(
        selector.SelectSelectorConfig(options=CURRENCIES),
    ),
    vol.Required(CONF_ADD_DISTRIBUTION_FEES, default=False): selector.BooleanSelector(
        selector.BooleanSelectorConfig(),
    ),
}

CONFIG_SCHEMA = vol.Schema(
    {vol.Optional(CONF_NAME, default=DEFAULT_NAME): str, **COMMON_SCHEMA}
)

OPTION_SCHEMA = vol.Schema({**COMMON_SCHEMA})

EXCHANGE_RATE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EXCHANGE_RATE, default=25): selector.NumberSelector(
            selector.NumberSelectorConfig(
                step=0.01, mode=selector.NumberSelectorMode.BOX, min=0
            )
        ),
        vol.Optional(CONF_EXCHANGE_RATE_SENSOR_ID): selector.EntitySelector(),
    }
)

DISTRIBTION_FEES_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DISTRIBUTION_FEE_H, default=648.62): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_DISTRIBUTION_FEE_L, default=438.09): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_TAX_FEE, default=28.30): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_SYSTEM_SERVICES_FEE, default=212.82): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_OTE_FEE, default=4.14): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_POZE_FEE, default=495.0): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=FEE_UNIT,
            )
        ),
        vol.Required(CONF_TAX, default=21.0): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1.0,
                step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="%",
            )
        ),
    }
)

default_low_tariff_hours = {
    DAY_MONDAY: [10, 12, 14, 17],
    DAY_TUESDAY: [10, 12, 14, 17],
    DAY_WEDNESDAY: [10, 12, 14, 17],
    DAY_THURSDAY: [10, 12, 14, 17],
    DAY_FRIDAY: [10, 12, 14, 17],
    DAY_SATURDAY: [10, 12, 14, 17],
    DAY_SUNDAY: [10, 12, 14, 17],
}

LOW_TARIFF_HOURS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_DISTRIBUTION_LOWER_PRICES_HOURS, default=default_low_tariff_hours
        ): selector.ObjectSelector(selector.ObjectSelectorConfig()),
    }
)


async def _next_step_1(user_input: Any) -> str:
    _LOGGER.debug(f"Next step: {user_input}")

    currency = user_input[CONF_CURRENCY]
    add_distribution_fees = user_input[CONF_ADD_DISTRIBUTION_FEES]
    if currency == CURRENCY_CZK:
        return "exchange_rate"

    if add_distribution_fees is True:
        return "distribution_fees"

    return None


async def _next_step_exchange_rate(user_input: Any) -> str:
    _LOGGER.debug(f"Next step exchange_rate: {user_input}")

    add_distribution_fees = user_input[CONF_ADD_DISTRIBUTION_FEES]
    return "distribution_fees" if add_distribution_fees is True else None


COMMON_FLOW: dict[str, SchemaFlowFormStep] = {
    "distribution_fees": SchemaFlowFormStep(
        DISTRIBTION_FEES_SCHEMA, next_step="low_tariff_hours"
    ),
    "low_tariff_hours": SchemaFlowFormStep(LOW_TARIFF_HOURS_SCHEMA),
    "exchange_rate": SchemaFlowFormStep(
        EXCHANGE_RATE_SCHEMA, next_step=_next_step_exchange_rate
    ),
}


CONFIG_FLOW: dict[str, SchemaFlowFormStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, next_step=_next_step_1),
    **COMMON_FLOW,
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep] = {
    "init": SchemaFlowFormStep(CONFIG_SCHEMA, next_step=_next_step_1),
    **COMMON_FLOW,
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    # Handle a config or options flow for Utility Meter.

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        # Return config entry title
        return cast(str, options[CONF_NAME]) if CONF_NAME in options else ""
