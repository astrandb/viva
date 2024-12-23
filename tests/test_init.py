"""Test initial setup."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viva import async_unload_entry
from custom_components.viva.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_integration

MOCK_CONFIG = {"id": "12"}


async def test_setup_entry(hass: HomeAssistant, bypass_get_data) -> None:
    """Test setup entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    await setup_integration(hass, entry)

    assert entry.state is ConfigEntryState.LOADED

    assert await async_unload_entry(hass, entry)
    assert DOMAIN not in hass.data


async def test_devices_created_count(
    hass: HomeAssistant,
    bypass_get_data,
) -> None:
    """Test that one device is created."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    await setup_integration(hass, config_entry)

    device_registry = dr.async_get(hass)

    assert len(device_registry.devices) == 1
