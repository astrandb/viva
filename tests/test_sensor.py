"""Provide tests for viva sensors."""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    snapshot_platform,
)
from syrupy.assertion import SnapshotAssertion

from custom_components.viva.const import DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration
from .const import ENTRY_ID, MOCK_CONFIG


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor(
    hass: HomeAssistant,
    bypass_get_data,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test sensor states."""

    mock_config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID
    )

    with patch("custom_components.viva.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    "data_file_name",
    ["station_166.json", "station_135.json", "station_88.json", "station_101.json"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_additional_stations(
    hass: HomeAssistant,
    bypass_get_data,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test states for additional stations."""

    mock_config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID
    )

    with patch("custom_components.viva.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize("data_file_name", ["station_101.json"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_several_samples_of_same_type(
    hass: HomeAssistant,
    bypass_get_data,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test a station with two water temperatures (at 3 m and at the bottom)."""

    mock_config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG, entry_id=ENTRY_ID
    )

    with patch("custom_components.viva.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    unique_ids = {entry.unique_id for entry in entries}
    # The first sample keeps the original unique id
    assert "101-Vattentemp" in unique_ids
    assert "101-Vattentemp-Vattentemp Botten" in unique_ids

    assert (
        hass.states.get("sensor.torshamnen_gbg_hamn_water_temperature").state == "9.6"
    )
    assert (
        hass.states.get("sensor.torshamnen_gbg_hamn_vattentemp_botten").state == "12.3"
    )
