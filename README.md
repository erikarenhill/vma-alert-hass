# VMA Alert for Home Assistant

This custom integration for Home Assistant provides alerts from the Swedish VMA (Viktigt Meddelande till Allmänheten) system.

## Features

- Real-time updates of VMA alerts
- Count of active VMA alerts
- Last update time sensor
- Test mode switch for using the test API

## Installation

### Using HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2. In the Home Assistant UI, go to HACS.
3. Click on "Integrations".
4. Click the three dots in the top right corner and select "Custom repositories".
5. Add this repository URL: `https://github.com/erikarenhill/vma-alert-hass`
6. Select "Integration" as the category.
7. Click "ADD".
8. Close the custom repositories window.
9. You should now see "VMA Alert" in the list of integrations. Click on it.
10. Click "INSTALL" and then "INSTALL" again in the pop-up window.
11. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/vma_alert_hass` directory to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, go to "Configuration" -> "Integrations".
2. Click the "+" button to add a new integration.
3. Search for "VMA Alert" and select it.
4. Follow the configuration steps. You can set the polling interval (default is 5 seconds).

## Usage

After installation and configuration, you'll have the following entities:

- `sensor.vma_alert`: Shows the latest VMA alert or "No active alerts".
- `sensor.active_vma_alerts`: Shows the count of active VMA alerts.
- `sensor.vma_last_update`: Shows the timestamp of the last update from the VMA API.
- `switch.vma_test_mode`: Toggles between the live API and the test API.

You can use these entities in your automations, scripts, and Lovelace UI.


## HOW TO SEND NOTIFICATION

Set up a new automation with trigger EVENT, type in "vma_new_alert" and leave the data field empty.

On actions, add a notification, then move over to manual yaml editing mode and copy paste this:

data:
  title: 'VMA Alert: {{ trigger.event.data.info[0].event }}'
  message: >
    {{ trigger.event.data.info[0].description }} Urgency: {{
    trigger.event.data.info[0].urgency }} Severity: {{
    trigger.event.data.info[0].severity }} Certainty: {{
    trigger.event.data.info[0].certainty }} Affected Area: {{
    trigger.event.data.info[0].area[0].areaDesc }}
action: notify.YOUR_NOTIFICATION_SERVICE_HERE # <--------- dont forget to change this

## HOW TO TEST

Go to developer tools, actions then trigger VMA Alert: simulate_vma_event
this will send a fake event on the bus for the vma_new_alert

OR

Switch on the Test mode, exposed as a control switch on the device for the integration.



