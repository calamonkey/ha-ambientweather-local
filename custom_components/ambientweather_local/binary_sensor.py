"""Battery binary sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AmbientLocalConfigEntry
from .const import DOMAIN
from .coordinator import AmbientLocalCoordinator

BATTERIES = (
    BinarySensorEntityDescription(key="inBattSta", translation_key="indoor_battery", device_class=BinarySensorDeviceClass.BATTERY),
    BinarySensorEntityDescription(key="outBattSta1", translation_key="outdoor_battery", device_class=BinarySensorDeviceClass.BATTERY),
    BinarySensorEntityDescription(key="outBattSta2", translation_key="outdoor2_battery", device_class=BinarySensorDeviceClass.BATTERY),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AmbientLocalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AmbientLocalBattery(coordinator, desc)
        for desc in BATTERIES
        if coordinator.data.get(desc.key) is not None
    )


class AmbientLocalBattery(CoordinatorEntity[AmbientLocalCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: AmbientLocalCoordinator, description: BinarySensorEntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, coordinator.unique_id)})

    @property
    def is_on(self) -> bool | None:
        """On means battery low (device class battery)."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return value.strip().lower() != "normal"
