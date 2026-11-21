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
        name="Átfolyás",
        translation_key="flow_rate",
        icon="mdi:water-pump",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="residualWaterProduction",
        name="Hátralévő vízmennyiség",
        translation_key="remaining_water_production",
        icon="mdi:water-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dailyWaterConsumption",
        name="Napi vízfogyasztás",
        translation_key="daily_water_consumption",
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="averageWeeklyWaterConsumption",
        name="Heti átlagos vízfogyasztás",
        translation_key="average_weekly_water_consumption",
        icon="mdi:chart-line",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="periodicWaterProduction",
        name="Víztermelés ebben az időszakban",
        translation_key="period_water_production",
        icon="mdi:water-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="operationDay",
        name="Üzemnap",
        translation_key="operation_day",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="remainingDay",
        name="Regenerálásig hátralévő napok",
        translation_key="days_until_regeneration",
        icon="mdi:calendar-alert",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="regenerationTimes",
        name="Regenerálások száma",
        translation_key="regeneration_count",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="backWashTimeRemaining",
        name="Visszamosásból hátralévő idő",
        translation_key="backwash_time_remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="absorbSaltTimeRemaining",
        name="Sóoldat-beszívásból hátralévő idő",
        translation_key="brine_draw_time_remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="saltTankRefillTimeRemaining",
        name="Sóoldattartály-feltöltésből hátralévő idő",
        translation_key="salt_tank_refill_time_remaining",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="washCountdownTime",
        name="Regenerálási visszaszámlálás",
        translation_key="regeneration_countdown",
        icon="mdi:timer-outline",
    ),
)

REGENERATION_STAGES = {
    0: ("Normal operation", "Normál működés"),
    1: ("Backwash", "Visszamosás"),
    2: ("Brine draw", "Sóoldat beszívása"),
    3: ("Brine tank refill", "Sóoldattartály feltöltése"),
    4: ("Fast rinse", "Gyors öblítés"),
    5: ("Valve closing", "Szelep zárása"),
    6: ("Salt dissolving", "Só oldódása"),
    7: ("Paused", "Szüneteltetve"),
    8: ("Paused", "Szüneteltetve"),
    9: ("Drain", "Leeresztés"),
    10: ("Recirculation", "Keringetés"),
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            WaterDeviceSensor(coordinator, config_entry, description)
            for description in SENSORS
        ]
        + [RegenerationStageSensor(coordinator, config_entry)]
    )


class WaterDeviceSensor(WaterDeviceEntity, SensorEntity):
    """A value reported in the device protocol data."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry, description):
        super().__init__(coordinator, config_entry)
        self.entity_description = description
        self._attr_unique_id = "{}_{}".format(
            config_entry.data["device_id"],
            description.key,
        )

    @property
    def native_value(self):
        """Return the current value for this sensor."""
        return self.coordinator.data["protocolData"].get(self.entity_description.key)


class RegenerationStageSensor(WaterDeviceEntity, SensorEntity):
    """Translate the device's station code into a readable cycle stage."""

    _attr_has_entity_name = True
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self.entity_description = SensorEntityDescription(
            key="regeneration_stage",
            name="Regenerálási fázis",
            translation_key="regeneration_stage",
            icon="mdi:water-sync",
        )
        self._attr_unique_id = "{}_regeneration_stage".format(
            config_entry.data["device_id"]
        )

    @property
    def native_value(self):
        """Return the localized name of the current valve station."""
        station = self.coordinator.data["protocolData"].get("station")
        try:
            station_code = int(station)
        except (TypeError, ValueError):
            return "Unknown stage"

        english, hungarian = REGENERATION_STAGES.get(
            station_code,
            (
                "Unknown stage ({})".format(station_code),
                "Ismeretlen lépés ({})".format(station_code),
            ),
        )
        language = (self.hass.config.language or "en").lower()
        if language.startswith("hu"):
            return hungarian
        return english

    @property
    def extra_state_attributes(self):
        """Expose the raw station code for the dashboard's stage indicator."""
        station = self.coordinator.data["protocolData"].get("station")
        try:
            is_regenerating = int(station) != 0
        except (TypeError, ValueError):
            is_regenerating = False
        return {
            "station_code": station,
            "is_regenerating": is_regenerating,
            "supports_vacation": self.coordinator.supports_vacation,
        }
