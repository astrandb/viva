"""Test initial setup."""

from aiohttp import ClientResponseError
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viva import async_unload_entry
from custom_components.viva.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_integration
from .const import ENTRY_ID, MOCK_CONFIG


async def test_setup_entry(hass: HomeAssistant, bypass_get_data) -> None:
    """Test setup entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID)
    await setup_integration(hass, entry)

    assert entry.state is ConfigEntryState.LOADED

    assert await async_unload_entry(hass, entry)
    assert DOMAIN not in hass.data


async def test_devices_created_count(
    hass: HomeAssistant,
    bypass_get_data,
) -> None:
    """Test that one device is created."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID)

    await setup_integration(hass, config_entry)

    device_registry = dr.async_get(hass)

    assert len(device_registry.devices) == 1


@pytest.mark.parametrize("exception", [ClientResponseError, TimeoutError])
async def test_api_error(hass: HomeAssistant, exception, mock_api) -> None:
    """Test for exceptions during data fetch."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID)
    entry.add_to_hass(hass)
    mock_api.side_effect = exception
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY
