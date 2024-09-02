"""Sensor platform for VMA Alert integration."""
from __future__ import annotations

from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VMA Alert sensors."""
    poll_interval = config_entry.data["poll_interval"]
    coordinator = VMADataUpdateCoordinator(hass, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        VMASensor(coordinator),
        VMACountSensor(coordinator)
    ], True)

class VMADataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching VMA data."""

    def __init__(self, hass: HomeAssistant, poll_interval: int):
        """Initialize."""
        super().__init__(
            hass,
            hass.logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.last_alert_id = None
        self.active_alerts = []

    async def _async_update_data(self):
        """Fetch data from API."""
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.sr.se/api/v2/vma/alerts?format=json") as response:
                    data = await response.json()

        alerts = data.get("alerts", [])
        self.active_alerts = [alert for alert in alerts if alert["msgType"] == "Alert"]
        
        if self.active_alerts and self.active_alerts[0]["identifier"] != self.last_alert_id:
            self.last_alert_id = self.active_alerts[0]["identifier"]
            return self.active_alerts[0]
        return None

class VMASensor(CoordinatorEntity, SensorEntity):
    """Representation of a VMA sensor."""

    def __init__(self, coordinator: VMADataUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "VMA Alert"
        self._attr_unique_id = f"{DOMAIN}_latest_alert"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["identifier"] if self.coordinator.data else "No active alerts"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "sent": self.coordinator.data["sent"],
                "description": self.coordinator.data["info"][0]["description"],
                "area": self.coordinator.data["info"][0]["area"][0]["areaDesc"],
            }
        return {}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data:
            self.hass.bus.fire("vma_alert_event", self.coordinator.data)
        super()._handle_coordinator_update()

class VMACountSensor(CoordinatorEntity, SensorEntity):
    """Representation of a VMA count sensor."""

    def __init__(self, coordinator: VMADataUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Active VMA Alerts"
        self._attr_unique_id = f"{DOMAIN}_active_alert_count"

    @property
    def state(self):
        """Return the number of active VMA alerts."""
        return len(self.coordinator.active_alerts)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "alerts": [
                {
                    "identifier": alert["identifier"],
                    "sent": alert["sent"],
                    "description": alert["info"][0]["description"],
                    "area": alert["info"][0]["area"][0]["areaDesc"],
                }
                for alert in self.coordinator.active_alerts
            ]
        }