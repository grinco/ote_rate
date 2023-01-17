"""Sample API Client."""
import logging
import asyncio
import socket
import aiohttp
import async_timeout
import aiohttp
from datetime import datetime
import logging

from .const import (
    HOUR_RESPONSE_NAME,
    COST_RESPONSE_NAME,
    OTE_CHART_DATA_ENDPOINT,
    OTE_BASE_URL,
)


TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class OteApiClient:
    """API client for OTE."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Sample API Client."""
        self._session = session

    async def async_get_costs_for_date(self, market: str, date: datetime) -> dict:
        """Get data from the API."""
        url = f"{OTE_BASE_URL}/{market}/{OTE_CHART_DATA_ENDPOINT}"
        params = {"report_date": date.strftime("%Y-%m-%d")}

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(url, params=params)
                return self.__parse_response_with_costs(date, await response.json())

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )

    def __parse_response_with_costs(self, date: datetime, json) -> dict:
        date_costs = dict()
        cost_axis = ""
        hour_axis = ""
        history_index = 0

        for key in json["axis"].keys():
            if json["axis"][key]["legend"] == COST_RESPONSE_NAME:
                cost_axis = key
            if json["axis"][key]["legend"] == HOUR_RESPONSE_NAME:
                hour_axis = key

        for values in json["data"]["dataLine"]:
            if values["title"] == COST_RESPONSE_NAME:
                for data in values["point"]:
                    history_index = int(data[hour_axis]) - 1
                    date_costs[history_index] = float(data[cost_axis])

        return date_costs
