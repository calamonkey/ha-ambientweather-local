"""Sensors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AmbientLocalConfigEntry
from .const import (
    DOMAIN,
    FC_TO_LUX,
    PRESSURE_UNITS,
    RAIN_UNITS,
    SOLAR_UNITS,
    TEMP_UNITS,
    WIND_UNITS,
)
from .coordinator import AmbientLocalCoordinator

MEAS = SensorStateClass.MEASUREMENT
TOTAL_INC = SensorStateClass.TOTAL_INCREASING


@dataclass(frozen=True, kw_only=True)
class AmbientLocalSensorDescription(SensorEntityDescription):
    """`kind` selects how the native unit is derived from the station settings."""

    kind: str = "fixed"  # fixed | temp | wind | rain | rain_rate | pressure | solar


SENSORS: tuple[AmbientLocalSensorDescription, ...] = (
    AmbientLocalSensorDescription(key="outTemp", translation_key="outdoor_temperature", kind="temp", device_class=SensorDeviceClass.TEMPERATURE, state_class=MEAS),
    AmbientLocalSensorDescription(key="inTemp", translation_key="indoor_temperature", kind="temp", device_class=SensorDeviceClass.TEMPERATURE, state_class=MEAS),
    AmbientLocalSensorDescription(key="outHumi", translation_key="outdoor_humidity", device_class=SensorDeviceClass.HUMIDITY, native_unit_of_measurement=PERCENTAGE, state_class=MEAS),
    AmbientLocalSensorDescription(key="inHumi", translation_key="indoor_humidity", device_class=SensorDeviceClass.HUMIDITY, native_unit_of_measurement=PERCENTAGE, state_class=MEAS),
    AmbientLocalSensorDescription(key="AbsPress", translation_key="absolute_pressure", kind="pressure", device_class=SensorDeviceClass.PRESSURE, state_class=MEAS),
    AmbientLocalSensorDescription(key="RelPress", translation_key="relative_pressure", kind="pressure", device_class=SensorDeviceClass.PRESSURE, state_class=MEAS),
    AmbientLocalSensorDescription(key="avgwind", translation_key="wind_speed", kind="wind", device_class=SensorDeviceClass.WIND_SPEED, state_class=MEAS),
    AmbientLocalSensorDescription(key="gustspeed", translation_key="wind_gust", kind="wind", device_class=SensorDeviceClass.WIND_SPEED, state_class=MEAS),
    AmbientLocalSensorDescription(key="dailygust", translation_key="max_daily_gust", kind="wind", device_class=SensorDeviceClass.WIND_SPEED, state_class=MEAS),
    AmbientLocalSensorDescription(key="windir", translation_key="wind_direction", native_unit_of_measurement=DEGREE, state_class=MEAS),
    AmbientLocalSensorDescription(key="solarrad", translation_key="solar_radiation", kind="solar", state_class=MEAS),
    AmbientLocalSensorDescription(key="uvi", translation_key="uv_index", state_class=MEAS),
    AmbientLocalSensorDescription(key="pm25out", translation_key="pm25_outdoor", device_class=SensorDeviceClass.PM25, native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, state_class=MEAS),
    AmbientLocalSensorDescription(key="pm25in", translation_key="pm25_indoor", device_class=SensorDeviceClass.PM25, native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, state_class=MEAS),
    AmbientLocalSensorDescription(key="rainofhourly", translation_key="hourly_rain_rate", kind="rain_rate", device_class=SensorDeviceClass.PRECIPITATION_INTENSITY, state_class=MEAS),
    AmbientLocalSensorDescription(key="eventrain", translation_key="event_rain", kind="rain", device_class=SensorDeviceClass.PRECIPITATION, state_class=SensorStateClass.TOTAL),
    AmbientLocalSensorDescription(key="rainofdaily", translation_key="daily_rain", kind="rain", device_class=SensorDeviceClass.PRECIPITATION, state_class=TOTAL_INC),
    AmbientLocalSensorDescription(key="rainofweekly", translation_key="weekly_rain", kind="rain", device_class=SensorDeviceClass.PRECIPITATION, state_class=TOTAL_INC),
    AmbientLocalSensorDescription(key="rainofmonthly", translation_key="monthly_rain", kind="rain", device_class=SensorDeviceClass.PRECIPITATION, state_class=TOTAL_INC),
    AmbientLocalSensorDescription(key="rainofyearly", translation_key="yearly_rain", kind="rain", device_class=SensorDeviceClass.PRECIPITATION, state_class=TOTAL_INC),
)


def native_unit(desc: AmbientLocalSensorDescription, units: dict[str, str]) -> str | None:
    """Unit the station reports this value in, per its station.htm settings."""
    match desc.kind:
        case "temp":
            return TEMP_UNITS.get(units["u_Temperature"])
        case "wind":
            return WIND_UNITS.get(units["unit_Wind"])
        case "rain":
            return RAIN_UNITS.get(units["u_Rainfall"])
        case "rain_rate":
            unit = RAIN_UNITS.get(units["u_Rainfall"])
            return f"{unit}/h" if unit else None
        case "pressure":
            return PRESSURE_UNITS.get(units["unit_Pressure"])
        case "solar":
            return "lx" if units["unit_Solar"] in ("0", "2") else "W/m²"
        case _:
            return desc.native_unit_of_measurement


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AmbientLocalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AmbientLocalSensor(coordinator, desc)
        for desc in SENSORS
        if coordinator.data.get(desc.key) is not None
    )


class AmbientLocalSensor(CoordinatorEntity[AmbientLocalCoordinator], SensorEntity):
    entity_description: AmbientLocalSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AmbientLocalCoordinator,
        description: AmbientLocalSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.unique_id)},
            name="AmbientWeather Station",
            manufacturer="Ambient Weather",
            configuration_url=f"http://{coordinator.client.host}",
        )
        if description.kind == "solar":
            self._update_solar_class()

    def _update_solar_class(self) -> None:
        lux = self.coordinator.units["unit_Solar"] in ("0", "2")
        self._attr_device_class = (
            SensorDeviceClass.ILLUMINANCE if lux else SensorDeviceClass.IRRADIANCE
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        return native_unit(self.entity_description, self.coordinator.units)

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        if self.entity_description.kind == "solar" and self.coordinator.units["unit_Solar"] == "2":
            value *= FC_TO_LUX  # foot-candles -> lux
        return value
