"""Euroclear water softener integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import WaterDeviceApi, WaterDeviceApiError
from .const import CONF_DEVICE_ID, CONF_TOKEN, DOMAIN

PLATFORMS = ["sensor", "binary_sensor", "button"]
_LOGGER = logging.getLogger(__name__)


class WaterDeviceCoordinator(DataUpdateCoordinator):
    """Fetches the selected water softener's state."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WaterDeviceApi,
        device_id: str,
    ) -> None:
        self.api = api
        self.device_id = device_id
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        try:
            return await self.api.async_get_device_state(self.device_id)
        except WaterDeviceApiError as err:
            raise UpdateFailed(str(err)) from err


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML (not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a configured water softener."""
    api = WaterDeviceApi(hass, entry.data[CONF_TOKEN])
    coordinator = WaterDeviceCoordinator(
        hass,
        api,
        entry.data[CONF_DEVICE_ID],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a configured water softener."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
