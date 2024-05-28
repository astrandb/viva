"""Provide tests for viva sensors."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viva.const import DOMAIN
from homeassistant.core import HomeAssistant

from . import setup_integration

MOCK_CONFIG = {"id": "12"}


@pytest.mark.parametrize(
    ("sensor", "expected_state", "device_class"),
    [
        ("sensor.forsmark_water_temperature", "2.1", "temperature"),
        ("sensor.forsmark_wind_strength", "3.6", "wind_speed"),
        ("sensor.forsmark_sealevel", "-33", "distance"),
    ],
)
async def test_sensor(
    hass: HomeAssistant,
    bypass_get_data,
    sensor: str,
    expected_state: str,
    device_class: str,
) -> None:
    """Test sensor."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    await setup_integration(hass, config_entry)

    state = hass.states.get(sensor)
    assert state is not None
    assert state.state == expected_state
    assert state.attributes["device_class"] == device_class
