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
   from the HA `custom_components/euroclear_water_softener/www` directory to
   `/config/www/euroclear-water-softener-card.js` (create `www` if needed).
4. In the dashboard's **Resources** page, add `/local/euroclear-water-softener-card.js`
   as a **JavaScript module**. The `/local/` URL maps to the HA configuration's
   `www` directory; it is not a `/hacsfiles/` URL. If Resources is not listed,
   enable **Advanced mode** in your user profile, then open the dashboard
   management menu.
5. Go to **Settings → Devices & services → Add integration** and select
   **Euroclear Water Softener**.
6. Enter the access token and, if prompted, choose your water softener.
7. Open the integration's **Configure** dialog to change its polling interval.
   The default is 60 seconds; allowed values are 15–3600 seconds. A shorter
   interval makes more cloud API requests.

When updating the integration, copy the updated card JavaScript to `www` again
if the card file changed in that release. Then hard-refresh the browser
dashboard (Ctrl+F5).

### Manual

Copy `custom_components/euroclear_water_softener` into the Home Assistant
`custom_components` directory and restart Home Assistant. Also copy
`custom_components/euroclear_water_softener/www/euroclear-water-softener-card.js`
to the configuration's `www` directory, add it as a JavaScript module resource
as described above, and add the integration from **Settings → Devices & services**.

## Entities

The integration creates sensors for flow rate, remaining water production,
daily and weekly water consumption, period production, operation day,
remaining days, regeneration count, regeneration-stage timers, and a
localized current regeneration stage. It also creates binary sensors for salt,
resin, filter, leak, and device fault alarms. Values are exposed as reported by
the API; no volume units are assumed because the API reports a separate
device-specific volume-unit code. Sensor names are translated according to
Home Assistant's language setting; English and Hungarian names are provided.

The **Start forced regeneration** button starts a regeneration cycle
immediately. The custom Lovelace card below asks for confirmation first. The
Home Assistant button entities remain directly callable from other cards,
automations, and service calls; those interfaces do not show the card's
confirmation dialog.

The card shows actions based on the reported device stage: while a regeneration
stage is active it offers **Advance to next stage**; while idle it offers
forced regeneration and, if supported by the model, holiday mode. When the
device is in holiday mode it offers an exit action. The card confirms each
operation before sending it.

## Lovelace card

After adding the JavaScript module resource, add a **Manual** card and use this
configuration. Replace the sample entity IDs with the IDs shown under
**Settings → Devices & services → Entities** for your device.

```yaml
type: custom:euroclear-water-softener-card
title: Vízlágyító
subtitle: Euroclear Midnight 25 HF P&P
regeneration_button: button.euroclear_midnight_25_hf_pp_start_forced_regeneration
advance_button: button.euroclear_midnight_25_hf_pp_advance_regeneration_stage
vacation_button: button.euroclear_midnight_25_hf_pp_enable_vacation_mode
exit_vacation_button: button.euroclear_midnight_25_hf_pp_exit_vacation_mode
stage_sensor: sensor.euroclear_midnight_25_hf_pp_regeneration_stage
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

Replace 'euroclear_midnight_25_hf_pp' with the name of your entity in the previous yaml example.

The card shows configured metrics, active alerts, the current stage and a
four-step progress display during backwash, brine draw, refill, and rinse.
During a running stage it offers the app's **Advance to next stage** action;
while idle it offers forced regeneration and (if supported by the model)
holiday mode. When the device is in holiday mode, it offers the exit action.
Every operation opens a confirmation dialog. Cancelling or clicking outside
the dialog does not send the command. Sensor history remains available in
standard Home Assistant history and statistics cards.

Replace every sample entity ID with its actual ID from **Settings → Devices &
services → Entities**. If an action fails, check the entity ID and Home
Assistant logs.

## Notes

- The token is stored in the Home Assistant config entry. Treat it as a
  password and do not share it.
- If the service expires or revokes the token, remove and add the integration
  again with a current token.
- The integration depends on the cloud API and requires internet access.
