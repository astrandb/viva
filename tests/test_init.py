"""Test initial setup."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viva import async_setup_entry, async_unload_entry
from custom_components.viva.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import setup_integration

MOCK_CONFIG = {"id": "12"}


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, bypass_get_data):
    """Test entry setup and unload."""

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id]["coordinator"], DataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_devices_created_count(
    hass: HomeAssistant,
    bypass_get_data,
    # mock_myuplink_client: MagicMock,
    # mock_config_entry: MockConfigEntry,
) -> None:
    """Test that one device is created."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    # assert await async_setup_entry(hass, config_entry)

    await setup_integration(hass, config_entry)

    device_registry = dr.async_get(hass)

    assert len(device_registry.devices) == 1
