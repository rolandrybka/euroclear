"""Control buttons for Euroclear water softeners."""

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .entity import WaterDeviceEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up control buttons for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ForceRegenerationButton(coordinator, config_entry)])


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
