"""Tests for config flow."""

from unittest.mock import patch

# from pytest_homeassistant_custom_component.common import MockConfigEntry
import pytest

from custom_components.viva.config_flow import CannotConnect, InvalidAuth
from custom_components.viva.const import DOMAIN
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .const import MOCK_CONFIG


@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.viva.async_setup_entry",
        return_value=True,
    ):
        yield


async def test_succesful_flow(hass: HomeAssistant, bypass_get_all_stations) -> None:
    """Test that we get the form and create the entry."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    # assert result["title"] == MOCK_CONFIG[CONF_PORT]
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


@pytest.mark.parametrize(
    ("exc", "key"),
    [
        (CannotConnect, "cannot_connect"),
        (InvalidAuth, "invalid_auth"),
        (Exception, "unknown"),
    ],
    ids=["cannot_connect", "invalid_auth", "other_exception"],
)
async def test_failed_flow(
    hass: HomeAssistant, bypass_get_all_stations, exc, key
) -> None:
    """Test failing flows."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch("custom_components.viva.config_flow.validate_input", side_effect=exc):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=MOCK_CONFIG
        )

    assert result["errors"] == {"base": key}
