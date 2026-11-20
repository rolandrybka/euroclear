"""Sensors for Euroclear water softeners."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN
from .entity import WaterDeviceEntity

SENSORS = (
    SensorEntityDescription(
        key="flowRate",
        name="Flow rate",
        icon="mdi:water-pump",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="residualWaterProduction",
        name="Remaining water production",
        icon="mdi:water-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dailyWaterConsumption",
        name="Daily water consumption",
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="averageWeeklyWaterConsumption",
        name="Average weekly water consumption",
        icon="mdi:chart-line",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="periodicWaterProduction",
        name="Water production this period",
        icon="mdi:water-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="operationDay",
        name="Operation day",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="remainingDay",
        name="Days until regeneration",
        icon="mdi:calendar-alert",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="regenerationTimes",
        name="Regeneration count",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="backWashTimeRemaining",
        name="Backwash time remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="absorbSaltTimeRemaining",
        name="Brine draw time remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="saltTankRefillTimeRemaining",
        name="Salt tank refill time remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="washCountdownTime",
        name="Regeneration countdown",
        icon="mdi:timer-outline",
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        WaterDeviceSensor(coordinator, config_entry, description)
        for description in SENSORS
    )


class WaterDeviceSensor(WaterDeviceEntity, SensorEntity):
    """A value reported in the device protocol data."""

    def __init__(self, coordinator, config_entry, description):
        super().__init__(coordinator, config_entry, description.name)
        self.entity_description = description
        self._attr_unique_id = "{}_{}".format(
            config_entry.data["device_id"],
            description.key,
        )

    @property
    def native_value(self):
        """Return the current value for this sensor."""
        return self.coordinator.data["protocolData"].get(self.entity_description.key)
