"""Coordinator for ViVa integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import override

from aiohttp import ClientResponseError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .pyviva import SingleStationObservation, ViVaAPI

_LOGGER = logging.getLogger(__name__)


@dataclass
class VivaRuntimeData:
    """Runtime data for the ViVa integration."""

    coordinator: VivaCoordinator


@dataclass
class VivaCoordinatorData:
    """Data class for storing coordinator data."""

    station_data: SingleStationObservation


type VivaConfigEntry = ConfigEntry[VivaRuntimeData]


class VivaCoordinator(DataUpdateCoordinator[VivaCoordinatorData]):
    """Data update coordinator for ViVa devices."""

    config_entry: VivaConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: VivaConfigEntry, api_client: ViVaAPI
    ) -> None:
        """Initialize the ViVa data update coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN} main",
            update_interval=timedelta(minutes=5),
            config_entry=entry,
        )

        self.api_client = api_client

    # @override
    # async def _async_setup(self) -> None:
    #     """Set up the coordinator."""

    @override
    async def _async_update_data(self) -> VivaCoordinatorData:
        """Fetch device state."""
        try:
            station_data = await self.api_client.get_station(
                self.config_entry.data[CONF_ID]
            )

        except ClientResponseError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="api_error",
                translation_placeholders={
                    "entry": self.config_entry.title,
                },
            ) from err
        except TimeoutError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="api_timeout",
                translation_placeholders={
                    "entry": self.config_entry.title,
                },
            ) from err

        return VivaCoordinatorData(station_data=station_data)
