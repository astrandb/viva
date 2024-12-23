"""Diagnostics support for ViVa."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import VivaConfigEntry

TO_REDACT: dict[str, Any] = {}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: VivaConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    return {
        "config_entry_data": async_redact_data(dict(config_entry.data), TO_REDACT),
        "coordinator_data": coordinator.data,
    }
