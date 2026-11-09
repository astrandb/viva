"""Platform for sensor integration."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    UnitOfLength,
    UnitOfRatio,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VivaConfigEntry, VivaCoordinator

SENSOR_TYPE_WIND = "wind"
SENSOR_TYPE_WIND_DIRECTION = "wind_direction"
SENSOR_TYPE_WIND_BEARING = "wind_bearing"
SENSOR_TYPE_LEVEL = "level"
SENSOR_TYPE_WATER_TEMP = "watertemp"
SENSOR_TYPE_AIR_HUMIDITY = "air"
SENSOR_TYPE_AIR_TEMP = "airtemp"
SENSOR_TYPE_SIGHT = "sight"
SENSOR_TYPE_WAVE = "wave"
SENSOR_TYPE_WAVE_DIRECTION = "wave_direction"
SENSOR_TYPE_WAVE_BEARING = "wave_bearing"

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class ViVaSensorDescription(SensorEntityDescription):
    """Class describing ViVa sensor entities."""

    type: str | None = None
    convert: Callable[[Any], Any] | None = None
    decimals: int = 1


WAVE_HEIGHT_SENSOR = ViVaSensorDescription(
    key="Våghöjd",
    type=SENSOR_TYPE_WAVE,
    device_class=SensorDeviceClass.DISTANCE,
    translation_key="wave_height",
    icon="mdi:waves",
    native_unit_of_measurement=UnitOfLength.METERS,
    state_class=SensorStateClass.MEASUREMENT,
)

WAVE_HEIGHT_DIRECTION_SENSOR = ViVaSensorDescription(
    key="Vågriktning",
    type=SENSOR_TYPE_WAVE_DIRECTION,
    icon="mdi:compass-outline",
    translation_key="wave_direction",
)

WAVE_BEARING_SENSOR = ViVaSensorDescription(
    key="Vågriktning_int",
    type=SENSOR_TYPE_WAVE_BEARING,
    native_unit_of_measurement=DEGREE,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:compass-outline",
    translation_key="wave_bearing",
    entity_registry_enabled_default=False,
)

WAVE_PERIOD_SENSOR = ViVaSensorDescription(
    key="Vågperiod",
    type=SENSOR_TYPE_WAVE,
    translation_key="wave_period",
    icon="mdi:waves",
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.MEASUREMENT,
)

LEVEL_SENSOR = ViVaSensorDescription(
    key="Vattenstånd",
    type=SENSOR_TYPE_LEVEL,
    device_class=SensorDeviceClass.DISTANCE,
    translation_key="sealevel",
    icon="mdi:ferry",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    state_class=SensorStateClass.MEASUREMENT,
)

LEVEL_SENSOR_RH2000 = ViVaSensorDescription(
    key="Vattenstånd",
    type=SENSOR_TYPE_LEVEL,
    device_class=SensorDeviceClass.DISTANCE,
    translation_key="sealevel_rh2000",
    icon="mdi:ferry",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    state_class=SensorStateClass.MEASUREMENT,
    entity_registry_enabled_default=False,
)

AVG_WIND_DIRECTION_SENSOR = ViVaSensorDescription(
    key="Vindriktning",
    type=SENSOR_TYPE_WIND_DIRECTION,
    icon="mdi:compass-outline",
    translation_key="wind_direction",
)

AVG_WIND_BEARING_SENSOR = ViVaSensorDescription(
    key="Vindriktning_int",
    type=SENSOR_TYPE_WIND_BEARING,
    native_unit_of_measurement=DEGREE,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:compass-outline",
    translation_key="wind_bearing",
    entity_registry_enabled_default=False,
)

AVG_WIND_SENSOR = ViVaSensorDescription(
    key="Medelvind",
    type=SENSOR_TYPE_WIND,
    device_class=SensorDeviceClass.WIND_SPEED,
    translation_key="wind_strength",
    native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
    suggested_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
    state_class=SensorStateClass.MEASUREMENT,
)

GUST_WIND_SENSOR = ViVaSensorDescription(
    key="Byvind",
    type=SENSOR_TYPE_WIND,
    device_class=SensorDeviceClass.WIND_SPEED,
    translation_key="gust_strength",
    native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
    suggested_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
    state_class=SensorStateClass.MEASUREMENT,
)

TEMP_SENSOR = ViVaSensorDescription(
    key="Vattentemp",
    type=SENSOR_TYPE_WATER_TEMP,
    device_class=SensorDeviceClass.TEMPERATURE,
    translation_key="water_temperature",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
)

AIR_TEMP_SENSOR = ViVaSensorDescription(
    key="temperatur",
    type=SENSOR_TYPE_AIR_TEMP,
    device_class=SensorDeviceClass.TEMPERATURE,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
)
AIR_HUMIDITY_SENSOR = ViVaSensorDescription(
    key="luftfuktighet",
    type=SENSOR_TYPE_AIR_HUMIDITY,
    device_class=SensorDeviceClass.HUMIDITY,
    native_unit_of_measurement=UnitOfRatio.PERCENTAGE,
    suggested_display_precision=0,
    state_class=SensorStateClass.MEASUREMENT,
)
SIGHT_SENSOR = ViVaSensorDescription(
    key="Sikt",
    type=SENSOR_TYPE_SIGHT,
    device_class=SensorDeviceClass.DISTANCE,
    icon="mdi:binoculars",
    translation_key="visibility",
    native_unit_of_measurement="m",
    suggested_display_precision=0,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VivaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []
    for obs in coordinator.data.station_data["Samples"]:
        obs2 = coordinator.data.station_data["Samples"][obs]
        if obs2["Type"] == SENSOR_TYPE_LEVEL:
            entities.append(ViVaSensor(coordinator, LEVEL_SENSOR, obs))
            entities.append(
                ViVaSensorSealevelRH2000(coordinator, LEVEL_SENSOR_RH2000, obs)
            )
        elif obs2["Type"] == SENSOR_TYPE_WIND and obs2["Name"] == "Medelvind":
            entities.append(ViVaSensor(coordinator, AVG_WIND_SENSOR, obs))
            entities.append(ViVaSensor(coordinator, AVG_WIND_DIRECTION_SENSOR, obs))
            entities.append(ViVaSensor(coordinator, AVG_WIND_BEARING_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_WIND and obs2["Name"] == "Byvind":
            entities.append(ViVaSensor(coordinator, GUST_WIND_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_WATER_TEMP:
            entities.append(ViVaSensor(coordinator, TEMP_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_AIR_TEMP:
            entities.append(ViVaSensor(coordinator, AIR_TEMP_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_AIR_HUMIDITY:
            entities.append(ViVaSensor(coordinator, AIR_HUMIDITY_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_SIGHT:
            entities.append(ViVaSensor(coordinator, SIGHT_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_WAVE and obs2["Name"] == "Våghöjd":
            entities.append(ViVaSensor(coordinator, WAVE_HEIGHT_SENSOR, obs))
            entities.append(ViVaSensor(coordinator, WAVE_HEIGHT_DIRECTION_SENSOR, obs))
            entities.append(ViVaSensor(coordinator, WAVE_BEARING_SENSOR, obs))
        elif obs2["Type"] == SENSOR_TYPE_WAVE and obs2["Name"] == "Vågperiod":
            entities.append(ViVaSensor(coordinator, WAVE_PERIOD_SENSOR, obs))
        else:
            _LOGGER.warning(
                "Unsupported sensor type %s on station %s",
                obs2["Type"],
                obs2["StationID"],
            )
            continue
        _LOGGER.debug(
            "Setting up sensor %s on station %s", obs2["Type"], obs2["StationID"]
        )

    # Some stations report several samples of the same kind, e.g. water temperature
    # at 3 m and at the bottom. The first one keeps the original unique id, so existing
    # entities are not affected; the others get their own unique id and name.
    seen_unique_ids: set[str] = set()
    for entity in entities:
        if entity.unique_id in seen_unique_ids:
            entity.set_additional_sample()
        seen_unique_ids.add(entity.unique_id)

    async_add_entities(entities)


class ViVaSensor(CoordinatorEntity[VivaCoordinator], SensorEntity):
    """Representation of a Sensor."""

    entity_description: ViVaSensorDescription
    sensor_id: str = ""

    def __init__(
        self,
        coordinator: VivaCoordinator,
        description: ViVaSensorDescription,
        sensor_id: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.sensor_id = sensor_id
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{self.coordinator.data.station_data['ID']}-{self.entity_description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.station_data["ID"])},
            name=self.coordinator.data.station_data["Name"],
            manufacturer="Sjöfartsverket",
            model="ViVa",
            configuration_url="https://viva.sjofartsverket.se",
            entry_type=DeviceEntryType.SERVICE,
        )

    def set_additional_sample(self) -> None:
        """Make this entity unique when the station has more samples of this kind.

        The sample name from the station (e.g. "Vattentemp Botten") is used in the
        unique id and as the entity name.
        """
        self._attr_unique_id = f"{self._attr_unique_id}-{self.sensor_id}"
        self._attr_name = self.sensor_id

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""

        retstr = self.coordinator.data.station_data["Samples"][self.sensor_id].get(
            "Value"
        )

        if retstr == "-":
            return None

        if self.entity_description.type == SENSOR_TYPE_WAVE:
            retval = retstr.split()
            return retval[1]

        if self.entity_description.type == SENSOR_TYPE_WIND:
            retval = retstr.split()
            return retval[1]

        if self.entity_description.type == SENSOR_TYPE_WAVE_DIRECTION:
            retval = retstr.split()
            return retval[0]

        if self.entity_description.type == SENSOR_TYPE_WAVE_BEARING:
            return self.coordinator.data.station_data["Samples"][self.sensor_id].get(
                "Heading"
            )

        if self.entity_description.type == SENSOR_TYPE_WIND_DIRECTION:
            retval = retstr.split()
            return retval[0]

        if self.entity_description.type == SENSOR_TYPE_WIND_BEARING:
            return self.coordinator.data.station_data["Samples"][self.sensor_id].get(
                "Heading"
            )

        if self.entity_description.type == SENSOR_TYPE_SIGHT:
            return retstr.replace(">", "")

        return retstr

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the extra state attributes of the sensor."""

        if self.entity_description.type == SENSOR_TYPE_LEVEL:
            return {
                "reference": self.coordinator.data.station_data["Samples"][
                    self.sensor_id
                ].get(
                    "WaterLevelReference",
                ),
                "offset": self.coordinator.data.station_data["Samples"][
                    self.sensor_id
                ].get(
                    "WaterLevelOffset",
                ),
            }

        return None

    @property
    def available(self) -> bool:
        """Return the availability of the entity."""

        return (
            self.coordinator.last_update_success
            and "Samples" in self.coordinator.data.station_data
            and self.sensor_id in self.coordinator.data.station_data["Samples"]
        )


class ViVaSensorSealevelRH2000(ViVaSensor):
    """Representation of a Sealevel sensor for reference level RH2000."""

    def __init__(
        self,
        coordinator: VivaCoordinator,
        description: ViVaSensorDescription,
        sensor_id: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, description, sensor_id)
        self._attr_unique_id = (
            f"{self.coordinator.data.station_data['ID']}-"
            f"{self.entity_description.key}-RH2000"
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""

        level = self.coordinator.data.station_data["Samples"][self.sensor_id].get(
            "Value"
        )
        if level == "-":
            return None

        if (
            self.coordinator.data.station_data["Samples"][self.sensor_id].get(
                "WaterLevelReference"
            )
            == "MVY"
        ):
            level = float(level) + float(
                self.coordinator.data.station_data["Samples"][self.sensor_id].get(
                    "WaterLevelOffset"
                    if self.coordinator.data.station_data["Samples"][
                        self.sensor_id
                    ].get("WaterLevelOffset")
                    is not None
                    else 0
                )
            )

        return float(level) if level is not None else None
