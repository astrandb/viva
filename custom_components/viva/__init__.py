"""The ViVa Weather integration."""

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import VivaConfigEntry, VivaCoordinator, VivaRuntimeData
from .pyviva import ViVaAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: VivaConfigEntry) -> bool:
    """Set up ViVa Weather from a config entry."""

    api_client = ViVaAPI(websession=async_get_clientsession(hass))
    coordinator = VivaCoordinator(hass, entry, api_client)
    entry.runtime_data = VivaRuntimeData(
        coordinator=coordinator,
    )
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: VivaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
