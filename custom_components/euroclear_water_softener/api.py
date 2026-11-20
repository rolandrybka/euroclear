"""Client for the waterdevice.net API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

API_URL = "https://api.waterdevice.net"
_LOGGER = logging.getLogger(__name__)


class WaterDeviceApiError(Exception):
    """An API request failed."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class WaterDeviceApi:
    """Small asynchronous API client."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        self._session = async_get_clientsession(hass)
        self._token = token.removeprefix("Bearer ").strip()

    async def _async_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send an authenticated API request."""
        try:
            async with self._session.request(
                method,
                API_URL + path,
                params=params,
                json=json_data,
                headers={"Authorization": "Bearer " + self._token},
            ) as response:
                if response.status >= 400:
                    _LOGGER.warning(
                        "Water device API returned HTTP %s for %s",
                        response.status,
                        path,
                    )
                    raise WaterDeviceApiError(
                        "Water device API returned HTTP {}".format(response.status),
                        response.status,
                    )
                if response.status == 204:
                    return None
                try:
                    return await response.json(content_type=None)
                except (ValueError, ClientError) as err:
                    raise WaterDeviceApiError(
                        "Water device API returned an invalid response"
                    ) from err
        except ClientError as err:
            raise WaterDeviceApiError("Unable to connect to the water device API") from err
        except asyncio.TimeoutError as err:
            raise WaterDeviceApiError("Timed out connecting to the water device API") from err

    async def async_get_devices(self) -> List[Dict[str, Any]]:
        """Return the devices available to this account."""
        families = await self._async_request(
            "GET",
            "/api/run-lucky/device/app/family/",
        )
        if families is not None and not isinstance(families, list):
            raise WaterDeviceApiError("The family list response was invalid")
        devices = []
        for family in families or []:
            if not isinstance(family, dict):
                raise WaterDeviceApiError("The family list response was invalid")
            family_id = family.get("id")
            if not family_id:
                continue
            family_devices = await self._async_request(
                "GET",
                "/api/run-lucky/device/app/family-device/get-list-by-family-id",
                params={"familyId": family_id},
            )
            if family_devices is not None and not isinstance(family_devices, list):
                raise WaterDeviceApiError("The device list response was invalid")
            devices.extend(family_devices or [])
        return devices

    async def async_get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Return the device's current protocol state."""
        result = await self._async_request(
            "POST",
            "/api/run-lucky/device/app/device-control/query-device-info-return-result",
            params={"id": device_id},
            json_data={},
        )
        if not isinstance(result, dict) or not isinstance(
            result.get("protocolData"), dict
        ):
            raise WaterDeviceApiError("The device state response was incomplete")
        return result

    async def async_force_regeneration(self, device_id: str) -> None:
        """Start a forced regeneration cycle."""
        await self._async_request(
            "POST",
            "/api/run-lucky/device/app/device-control/forced-regeneration",
            params={"id": device_id},
            json_data={},
        )
