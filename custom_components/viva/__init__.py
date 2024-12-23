"""The ViVa Weather integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging

from aiohttp import ClientResponseError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .pyviva import ViVaAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

type VivaConfigEntry = ConfigEntry[VivaData]


@dataclass
class VivaData:
    """Runtime data for Viva integration."""

    api: ViVaAPI
    coordinator: DataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: VivaConfigEntry) -> bool:
    """Set up ViVa Weather from a config entry."""

    entry.runtime_data = VivaData(
        api=ViVaAPI(websession=async_get_clientsession(hass)), coordinator=None
    )

    coordinator = await get_coordinator(hass, entry)
    if not coordinator.last_update_success:
        await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: VivaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def get_coordinator(
    hass: HomeAssistant,
    entry: VivaConfigEntry,
) -> DataUpdateCoordinator:
    """Get the data update coordinator."""
    if entry.runtime_data.coordinator:
        return entry.runtime_data.coordinator

    async def async_fetch():
        api = entry.runtime_data.api
        try:
            async with asyncio.timeout(10):
                return await api.get_station(entry.data["id"])
        except ClientResponseError as exc:
            _LOGGER.warning("API fetch failed. Status: %s, - %s", exc.code, exc.message)
            raise UpdateFailed(exc) from exc
        except TimeoutError as error:
            _LOGGER.warning("Timeout during coordinator fetch")
            raise UpdateFailed(error) from error

    entry.runtime_data.coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_fetch,
        update_interval=timedelta(minutes=5),
    )
    await entry.runtime_data.coordinator.async_refresh()
    return entry.runtime_data.coordinator
