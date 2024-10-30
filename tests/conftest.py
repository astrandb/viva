"""pytest fixtures."""

from unittest.mock import patch

import pytest

# pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture(hass):
    """Skip calls to get data from API."""
    with patch("custom_components.viva.pyviva.ViVaAPI.get_station"):
        yield
