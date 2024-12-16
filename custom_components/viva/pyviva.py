"""pyviva - library for viva integration for Home Assistant."""

# Move to pypi.org when stable

from __future__ import annotations

import logging
from typing import Any, TypedDict

from aiohttp import ClientResponse, ClientResponseError, ClientSession

# import httpx

API_URL = "https://services.viva.sjofartsverket.se:8080/output/vivaoutputservice.svc/vivastation"

# Old web: http://vivadisplay.sjofartsverket.se/#/station/166

_LOGGER = logging.getLogger(__name__)


class StationModel(TypedDict):
    """Data model for Station."""

    ID: int
    Name: str
    Lat: float
    Lon: float


class Station:
    """Station class."""

    def __init__(self, raw_data: StationModel) -> None:
        """Init the class."""
        self.raw_data = raw_data

    @property
    def id(self) -> int:
        """Return id."""
        return self.raw_data["ID"]

    @property
    def name(self) -> str:
        """Return name."""
        return self.raw_data["Name"]

    @property
    def lat(self) -> float:
        """Return lattitude."""
        return self.raw_data["Lat"]

    @property
    def lon(self) -> float:
        """Return longitude."""
        return self.raw_data["Lon"]


class SampleModel(TypedDict):
    """Data model for sample observation."""

    Name: str
    Value: str
    Heading: int
    Unit: str
    Type: str
    Trend: str
    Msg: str
    Calm: int
    Updated: str
    StationID: int
    Quality: str
    WaterLevelReference: Any
    WaterLevelOffset: Any


class Observation:
    """Data model for observation."""

    def __init__(self, raw_data: SampleModel) -> None:
        """Init the class."""
        self.raw_data = raw_data

    @property
    def name(self) -> str:
        """Return name."""
        return self.raw_data["Name"]


class SingleStationObservation:
    """Class to get data from observation."""

    def __init__(self, raw_data: Observation) -> None:
        """Init the class."""
        self.raw_data = raw_data


class ViVaAPI:
    """Class to get data from ViVa API v1."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialize."""
        self._websession = websession

    async def request(self, method, station="", **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
            kwargs.pop("headers")

        res = await self._websession.request(
            method,
            f"{API_URL}/{station}",
            **kwargs,
            headers=headers,
        )
        res.raise_for_status()
        return res

    async def get_data(self):
        """Get data from api."""
        try:
            res = await self.request("GET")
            return await res.json()
        except ClientResponseError as exc:
            _LOGGER.error(
                "API get_data failed. Status: %s, - %s", exc.code, exc.message
            )

    async def get_all_stations(self) -> list[Station]:
        """Return all stations."""
        try:
            resp = await self.request("get", "")
            data = await resp.json()
            result = data["GetStationsResult"]["Stations"]
            return [Station(station_data) for station_data in result]
        except ClientResponseError as exc:
            _LOGGER.error(
                "API get_data failed. Status: %s, - %s", exc.code, exc.message
            )
        return []

    async def get_station(self, id_no: int) -> SingleStationObservation:
        """Return data from one station."""

        resp = await self.request("get", f"/{id_no}")
        data = await resp.json()
        result = data["GetSingleStationResult"]
        res = {}
        for sample in data["GetSingleStationResult"]["Samples"]:
            res[sample["Name"]] = sample
        result["Samples"] = res

        return result
