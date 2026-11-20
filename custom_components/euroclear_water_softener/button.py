"""Control buttons for Euroclear water softeners."""

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .entity import WaterDeviceEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up control buttons for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            ForceRegenerationButton(coordinator, config_entry),
            AdvanceRegenerationButton(coordinator, config_entry),
            VacationModeButton(coordinator, config_entry),
            ExitVacationModeButton(coordinator, config_entry),
        ]
    )


class ForceRegenerationButton(WaterDeviceEntity, ButtonEntity):
    """Start a forced regeneration cycle."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "Start forced regeneration")
        self._attr_unique_id = "{}_forced_regeneration".format(
            config_entry.data["device_id"]
        )
        self._attr_icon = "mdi:water-sync"

    async def async_press(self):
        """Request forced regeneration and refresh the device state."""
        await self.coordinator.api.async_force_regeneration(self._device_id)
        await self.coordinator.async_request_refresh()


class AdvanceRegenerationButton(WaterDeviceEntity, ButtonEntity):
    """Advance the active regeneration cycle to its next stage."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "Advance regeneration stage")
        self._attr_unique_id = "{}_advance_regeneration".format(
            config_entry.data["device_id"]
        )
        self._attr_icon = "mdi:skip-forward"

    async def async_press(self):
        """Advance the cycle using the app's forced-switch command."""
        await self.coordinator.api.async_advance_regeneration(self._device_id)
        await self.coordinator.async_request_refresh()


class VacationModeButton(WaterDeviceEntity, ButtonEntity):
    """Enable vacation mode."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "Enable vacation mode")
        self._attr_unique_id = "{}_enable_vacation_mode".format(
            config_entry.data["device_id"]
        )
        self._attr_icon = "mdi:bag-suitcase"

    async def async_press(self):
        """Enable vacation mode and refresh the device state."""
        await self.coordinator.api.async_set_vacation_mode(self._device_id)
        await self.coordinator.async_request_refresh()


class ExitVacationModeButton(WaterDeviceEntity, ButtonEntity):
    """Exit vacation mode."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "Exit vacation mode")
        self._attr_unique_id = "{}_exit_vacation_mode".format(
            config_entry.data["device_id"]
        )
        self._attr_icon = "mdi:home"

    async def async_press(self):
        """Exit vacation mode and refresh the device state."""
        await self.coordinator.api.async_exit_vacation_mode(self._device_id)
        await self.coordinator.async_request_refresh()
