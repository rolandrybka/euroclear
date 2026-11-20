"""Config flow for Euroclear water softeners."""

import logging

import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries

from .api import WaterDeviceApi, WaterDeviceApiError
from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up the integration using an existing API access token."""

    VERSION = 1

    def __init__(self):
        self._token = None
        self._devices = {}

    async def async_step_user(self, user_input=None):
        """Validate a token and discover available devices."""
        errors = {}
        if user_input is not None:
            self._token = user_input[CONF_TOKEN].strip()
            if self._token.lower().startswith("bearer "):
                self._token = self._token[7:].strip()
            api = WaterDeviceApi(self.hass, self._token)
            try:
                devices = await api.async_get_devices()
            except WaterDeviceApiError as err:
                _LOGGER.warning("Unable to validate water device token: %s", err)
                errors["base"] = (
                    "invalid_auth"
                    if err.status_code in (401, 403)
                    else "cannot_connect"
                )
            except ClientError as err:
                _LOGGER.warning("Unable to connect while validating token: %s", err)
                errors["base"] = "cannot_connect"
            else:
                self._devices = {
                    str(device["deviceId"]): device
                    for device in devices
                    if device.get("deviceId")
                }
                if not self._devices:
                    errors["base"] = "no_devices"
                elif len(self._devices) == 1:
                    device_id, device = next(iter(self._devices.items()))
                    return await self._create_entry(device_id, device)
                else:
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )

    async def async_step_device(self, user_input=None):
        """Let the user choose a device when the account has several."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            return await self._create_entry(device_id, self._devices[device_id])

        choices = {
            device_id: device.get("name") or device_id
            for device_id, device in self._devices.items()
        }
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(choices)}
            ),
        )

    async def _create_entry(self, device_id, device):
        """Create a config entry for the selected device."""
        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured()
        name = device.get("name") or "Euroclear water softener"
        return self.async_create_entry(
            title=name,
            data={
                CONF_TOKEN: self._token,
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_NAME: name,
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow for an existing device."""
        return EuroclearWaterSoftenerOptionsFlow(config_entry)


class EuroclearWaterSoftenerOptionsFlow(config_entries.OptionsFlow):
    """Configure the device polling interval."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Set the polling interval in seconds."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                        ),
                    )
                }
            ),
        )
