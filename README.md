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
3. Copy `custom_components/euroclear_water_softener/www/euroclear-water-softener-card.js`
   from the installed integration to the Home Assistant configuration's `www`
   directory (create it if needed).
4. In **Settings → Dashboards → Resources**, add `/local/euroclear-water-softener-card.js`
   as a JavaScript module resource. If the Resources menu is not available, open
   the dashboard in edit mode and manage resources from its menu.
5. Go to **Settings → Devices & services → Add integration** and select
   **Euroclear Water Softener**.
6. Enter the access token and, if prompted, choose your water softener.

When updating the integration, copy the updated card JavaScript to `www` again
if the card file changed in that release. Then reload the browser dashboard.

### Manual

Copy `custom_components/euroclear_water_softener` into the Home Assistant
`custom_components` directory and restart Home Assistant. Also copy
`custom_components/euroclear_water_softener/www/euroclear-water-softener-card.js`
to the configuration's `www` directory, add it as a JavaScript module resource
as described above, and add the integration from **Settings → Devices & services**.

## Entities

The integration creates sensors for flow rate, remaining water production,
daily and weekly water consumption, period production, operation day,
remaining days, regeneration count, and regeneration-stage timers. It also
creates binary sensors for salt, resin, filter, leak, and device fault alarms.
Values are exposed as reported by the API; no volume units are assumed because
the API reports a separate device-specific volume-unit code.

The **Start forced regeneration** button starts a regeneration cycle
immediately. The custom Lovelace card below asks for confirmation first. The
integration's regular Home Assistant button entity remains directly callable
from other cards, automations, and service calls; those interfaces do not show
the card's confirmation dialog.

## Lovelace card

After adding the JavaScript module resource, add a **Manual** card and use this
configuration. Replace the sample entity IDs with the IDs shown under
**Settings → Devices & services → Entities** for your device.

```yaml
type: custom:euroclear-water-softener-card
title: Vízlágyító
subtitle: Euroclear Midnight 25 HF P&P
regeneration_button: button.euroclear_midnight_25_hf_pp_start_forced_regeneration
metrics:
  - entity: sensor.euroclear_midnight_25_hf_pp_flow_rate
    label: Átfolyás
    icon: mdi:water-pump
  - entity: sensor.euroclear_midnight_25_hf_pp_remaining_water_production
    label: Hátralévő víz
    icon: mdi:water-outline
  - entity: sensor.euroclear_midnight_25_hf_pp_daily_water_consumption
    label: Mai fogyasztás
    icon: mdi:water
  - entity: sensor.euroclear_midnight_25_hf_pp_days_until_regeneration
    label: Regenerálásig hátralévő napok
    icon: mdi:calendar-alert
alerts:
  - entity: binary_sensor.euroclear_midnight_25_hf_pp_salt_shortage_alarm
    label: Sóhiány
  - entity: binary_sensor.euroclear_midnight_25_hf_pp_water_leakage
    label: Vízszivárgás
```

The card shows configured metrics, active alerts, and a forced-regeneration
control. Pressing the control opens a confirmation dialog describing the
expected 5–6 hour cycle before it sends the command. Cancelling or clicking
outside the dialog does not start regeneration. Sensor history remains
available in standard Home Assistant history and statistics cards.

## Notes

- The token is stored in the Home Assistant config entry. Treat it as a
  password and do not share it.
- If the service expires or revokes the token, remove and add the integration
  again with a current token.
- The integration depends on the cloud API and requires internet access.
