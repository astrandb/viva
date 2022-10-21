"""Config flow for ViVa Weather integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
import httpx
import voluptuous as vol

from .const import DOMAIN
from .pyviva import ViVaAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = (
    vol.Schema(
        {
            vol.Required("id"): str,
        }
    ),
)

stations = [
    SelectOptionDict(value="123", label="Value 123"),
    SelectOptionDict(value="176", label="Stockholm (SMHI)"),
    SelectOptionDict(value="126", label="Value 126"),
]


class ViVaHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, id_num: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = ViVaHub(data["id"])

    if not await hub.authenticate(data["id"]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Sjöfartsverket ViVa"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ViVa Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        viva_api = ViVaAPI(websession=httpx.AsyncClient())
        # station_list3 = await API.get_all_stations()
        station_list4 = [
            SelectOptionDict(value=str(st.id), label=st.name)
            for st in await viva_api.get_all_stations()
        ]

        if user_input is None:

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("id"): SelectSelector(
                            SelectSelectorConfig(options=station_list4)
                        ),
                    }
                ),
                errors={},
            )

        errors = {}
        try:
            await validate_input(self.hass, user_input)
            # info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            title = next(
                (item for item in station_list4 if item["value"] == user_input["id"]),
                None,
            )["label"]
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("id"): SelectSelector(
                        SelectSelectorConfig(options=station_list4)
                    ),
                }
            ),
            errors={},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
