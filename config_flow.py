from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.const import (
    MAJOR_VERSION,
    MINOR_VERSION,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import (
    CONF_CURRENCY,
    DOMAIN,
    CONF_EXCHANGE_RATE,
    CONF_EXCHANGE_RATE_SENSOR_ID,
    CURRENCY_CZK,
    CURRENCY_EUR,
    CONF_CHARGE,
    DEFAULT_NAME,
)


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


async def _next_step(user_input: Any) -> str:
    currency = user_input[CONF_CURRENCY]
    return currency if currency in CONFIG_FLOW else None


COMMON_FLOW: dict[str, SchemaFlowFormStep] = {
    CURRENCY_CZK: SchemaFlowFormStep(EXCHANGE_RATE_SCHEMA),
}


CONFIG_FLOW: dict[str, SchemaFlowFormStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, next_step=_next_step),
    **COMMON_FLOW,
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep] = {
    "init": SchemaFlowFormStep(CONFIG_SCHEMA, next_step=_next_step),
    **COMMON_FLOW,
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    # Handle a config or options flow for Utility Meter.

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        # Return config entry title
        return cast(str, options[CONF_NAME]) if CONF_NAME in options else ""
