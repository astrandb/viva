"""Config flow for ViVa Weather integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

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
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        viva_api = ViVaAPI(websession=async_get_clientsession(self.hass))
        station_list = [
            SelectOptionDict(value=str(st.id), label=st.name)
            for st in await viva_api.get_all_stations()
        ]

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("id"): SelectSelector(
                            SelectSelectorConfig(options=station_list)
                        ),
                    }
                ),
                errors={},
            )

        errors = {}
        await self.async_set_unique_id(user_input["id"])
        self._abort_if_unique_id_configured()

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
            station = next(
                (item for item in station_list if item["value"] == user_input["id"]),
                None,
            )
            title = station["label"] if station is not None else ""
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("id"): SelectSelector(
                        SelectSelectorConfig(options=station_list)
                    ),
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
