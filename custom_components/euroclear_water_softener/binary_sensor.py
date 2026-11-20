"""Alarm and fault sensors for Euroclear water softeners."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .entity import WaterDeviceEntity

BINARY_SENSORS = (
    BinarySensorEntityDescription(
        key="saltShortageAlarm",
        name="Salt shortage alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="saltShortageReminder",
        name="Salt shortage reminder",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="resinReplacementReminder",
        name="Resin replacement reminder",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="filterMaterialReminder",
        name="Filter material reminder",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="waterLeakage",
        name="Water leakage",
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    BinarySensorEntityDescription(
        key="clockChipFault",
        name="Clock chip fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="multiplePositionSignalFault",
        name="Multiple position signal fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="noPositionSignalFault",
        name="No position signal fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="memoryErrorFault",
        name="Memory error fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up binary sensors for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        WaterDeviceBinarySensor(coordinator, config_entry, description)
        for description in BINARY_SENSORS
    )


class WaterDeviceBinarySensor(WaterDeviceEntity, BinarySensorEntity):
    """A boolean alarm or fault value."""

    def __init__(self, coordinator, config_entry, description):
        super().__init__(coordinator, config_entry, description.name)
        self.entity_description = description
        self._attr_unique_id = "{}_{}".format(
            config_entry.data["device_id"],
            description.key,
        )

    @property
    def is_on(self):
        """Return whether this alarm or fault is active."""
        return bool(
            self.coordinator.data["protocolData"].get(
                self.entity_description.key,
                False,
            )
        )
