# Euroclear Water Softener

Home Assistant integration for Euroclear water softeners exposed by
`app.waterdevice.net`. It polls the cloud API every 60 seconds and provides
water-use and regeneration sensors, alarm/fault binary sensors, and a button
to start a forced regeneration cycle.

## Requirements

- Home Assistant 2023.2.0 or later
- An access token accepted by `api.waterdevice.net`

The integration uses the Home Assistant-provided `aiohttp` session and has no
additional Python dependencies. It accepts an existing access token; it does
not ask for or store your web-app password.

## Installation

### HACS

1. Add this repository as a custom repository in HACS, using the **Integration**
   category.
2. Install **Euroclear Water Softener** and restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and select
   **Euroclear Water Softener**.
4. Enter the access token and, if prompted, choose your water softener.

### Manual

Copy `custom_components/euroclear_water_softener` into the Home Assistant
`custom_components` directory, restart Home Assistant, and add the integration
from **Settings → Devices & services**.

## Entities

The integration creates sensors for flow rate, remaining water production,
daily and weekly water consumption, period production, operation day,
remaining days, regeneration count, and regeneration-stage timers. It also
creates binary sensors for salt, resin, filter, leak, and device fault alarms.
Values are exposed as reported by the API; no volume units are assumed because
the API reports a separate device-specific volume-unit code.

The **Start forced regeneration** button starts a regeneration cycle
immediately. Use it only when appropriate for your device.

All sensor history is available to standard Home Assistant cards, including
History Graph and Statistics Graph cards. Select the integration's sensors in
the card editor to build a dashboard.

## Notes

- The token is stored in the Home Assistant config entry. Treat it as a
  password and do not share it.
- If the service expires or revokes the token, remove and add the integration
  again with a current token.
- The integration depends on the cloud API and requires internet access.
