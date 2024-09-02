"""Sensor platform for VMA Alert integration."""
from __future__ import annotations

from datetime import timedelta, datetime
import logging
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .entity import VMAEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VMA Alert sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        VMASensor(coordinator, config_entry),
        VMACountSensor(coordinator, config_entry),
        VMALastUpdateSensor(coordinator, config_entry),
    ], True)

class VMADataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching VMA data."""

    def __init__(self, hass: HomeAssistant, poll_interval: int):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.data = {"latest_alert": None, "active_alerts": [], "last_update": None}
        self.test_mode = False
        self.last_alert_id = None

    async def _async_update_data(self):
        """Fetch data from API."""
        api_url = "https://vmaapi.sr.se/api/v2/alerts?format=json"
        if self.test_mode:
            api_url = "https://vmaapi.sr.se/TestApi/v2/alerts?format=json"

        _LOGGER.debug("Fetching VMA data from %s (Test mode: %s)", api_url, self.test_mode)

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            _LOGGER.error("Error connecting to VMA API: %s", response.status)
                            raise ConfigEntryNotReady(f"Error connecting to VMA API: {response.status}")
                        data = await response.json()

            _LOGGER.debug("Received VMA data: %s", data)

            alerts = data.get("alerts", [])
            active_alerts = [alert for alert in alerts if alert["msgType"] == "Alert"]
            
            _LOGGER.debug("Processed %d active alerts", len(active_alerts))

            latest_alert = active_alerts[0] if active_alerts else None
            if latest_alert and latest_alert["identifier"] != self.last_alert_id:
                self.last_alert_id = latest_alert["identifier"]
                self.hass.bus.async_fire("vma_new_alert", latest_alert)
                _LOGGER.info("New VMA alert detected: %s", latest_alert["identifier"])

            return {
                "latest_alert": latest_alert,
                "active_alerts": active_alerts,
                "last_update": dt_util.utcnow()
            }
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to VMA API: %s", err)
            raise ConfigEntryNotReady(f"Error connecting to VMA API: {err}") from err

    async def set_test_mode(self, test_mode: bool):
        """Set the test mode and refresh data."""
        _LOGGER.info("Setting VMA test mode to: %s", test_mode)
        self.test_mode = test_mode
        await self.async_refresh()

class VMASensor(VMAEntity, SensorEntity):
    """Representation of a VMA sensor."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "VMA Alert"
        self._attr_unique_id = f"{DOMAIN}_latest_alert"

    @property
    def state(self):
        """Return the state of the sensor."""
        latest_alert = self.coordinator.data["latest_alert"]
        return latest_alert["identifier"] if latest_alert else "No active alerts"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        latest_alert = self.coordinator.data["latest_alert"]
        if latest_alert:
            return {
                "sent": latest_alert["sent"],
                "description": latest_alert["info"][0]["description"],
                "area": latest_alert["info"][0]["area"][0]["areaDesc"],
            }
        return {}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        latest_alert = self.coordinator.data["latest_alert"]
        if latest_alert:
            self.hass.bus.fire("vma_alert_event", latest_alert)
        super()._handle_coordinator_update()

class VMACountSensor(VMAEntity, SensorEntity):
    """Representation of a VMA count sensor."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "Active VMA Alerts"
        self._attr_unique_id = f"{DOMAIN}_active_alert_count"

    @property
    def state(self):
        """Return the number of active VMA alerts."""
        return len(self.coordinator.data["active_alerts"])

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
                for alert in self.coordinator.data["active_alerts"]
            ]
        }

class VMALastUpdateSensor(VMAEntity, SensorEntity):
    """Representation of a VMA last update sensor."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "VMA Last Update"
        self._attr_unique_id = f"{DOMAIN}_last_update"

    @property
    def state(self):
        """Return the last update time."""
        last_update = self.coordinator.data["last_update"]
        if last_update:
            return last_update.isoformat()
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        last_update = self.coordinator.data["last_update"]
        if last_update:
            return {
                "last_update_timestamp": last_update.timestamp(),
                "last_update_local": last_update.astimezone().isoformat(),
            }
        return {}