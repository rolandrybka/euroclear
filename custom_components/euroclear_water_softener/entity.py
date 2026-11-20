"""Base entity for Euroclear water softeners."""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN


class WaterDeviceEntity(CoordinatorEntity):
    """Common device and coordinator attributes."""

    def __init__(self, coordinator, config_entry, name):
        super().__init__(coordinator)
        self._device_id = config_entry.data[CONF_DEVICE_ID]
        self._device_name = config_entry.data[CONF_DEVICE_NAME]
        self._attr_name = "{} {}".format(self._device_name, name)
        self._attr_unique_id = "{}_{}".format(
            self._device_id,
            name.lower().replace(" ", "_"),
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Euroclear",
            model="Midnight 25 HF P&P",
        )
