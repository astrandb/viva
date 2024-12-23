"""pytest fixtures."""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.viva.pyviva import SingleStationObservation
from homeassistant.core import HomeAssistant
from homeassistant.util.json import json_loads


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture(name="load_default_station")
def load_default_station_fixture() -> SingleStationObservation:
    """Load data for default station."""
    # print(json_loads(load_fixture("station_12a.json")))
    return json_loads(load_fixture("station_12a.json"))


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture(
    hass: HomeAssistant,
    load_default_station: SingleStationObservation,
):
    """Skip calls to get data from API."""
    with patch(
        "custom_components.viva.pyviva.ViVaAPI.get_station",
        return_value=load_default_station,
    ):
        yield
