"""Data coordinator for VMA Alert integration."""
from datetime import timedelta
import logging
import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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

        # Reset data when changing test mode
        self.data = {"latest_alert": None, "active_alerts": [], "last_update": None}
        self.last_alert_id = None

        await self.async_refresh()