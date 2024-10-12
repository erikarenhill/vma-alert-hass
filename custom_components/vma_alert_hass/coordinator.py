"""Data coordinator for VMA Alert integration."""
from datetime import timedelta
import logging
import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCB_GEO_CODES

_LOGGER = logging.getLogger(__name__)

class VMADataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching VMA data."""

    def __init__(self, hass: HomeAssistant, poll_interval: int, geo_code: str | None):
        """Initialize."""
        _LOGGER.debug("Initializing VMADataUpdateCoordinator with poll_interval: %s, geo_code: %s", poll_interval, geo_code)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.data = {"latest_alert": None, "active_alerts": [], "last_update": None}
        self.test_mode = False
        self.last_alert_ids = set()
        self.geo_code = geo_code
        self.area_name = SCB_GEO_CODES.get(geo_code, "Hela Sverige") if geo_code else "Hela Sverige"
        _LOGGER.debug("VMADataUpdateCoordinator initialized for area: %s", self.area_name)

    async def _async_update_data(self):
        """Fetch data from API."""
        base_url = "https://vmaapi.sr.se/api/v2/alerts"
        if self.test_mode:
            base_url = "https://vmaapi.sr.se/TestApi/v2/alerts"

        _LOGGER.debug("Fetching VMA data (Test mode: %s) for geo_code: %s", self.test_mode, self.geo_code)

        try:
            async with async_timeout.timeout(30):
                async with aiohttp.ClientSession() as session:
                    if self.geo_code:
                        url = f"{base_url}/{self.geo_code}"
                    else:
                        url = base_url
                    _LOGGER.debug("Fetching data from URL: %s", url)
                    alerts = await self._fetch_alerts(session, url)

            _LOGGER.debug("Received VMA data: %s", alerts)

            active_alerts = [alert for alert in alerts if alert["msgType"] == "Alert"]
            
            _LOGGER.debug("Processed %d active alerts", len(active_alerts))

            new_alerts = [alert for alert in active_alerts if alert["identifier"] not in self.last_alert_ids]
            
            for new_alert in new_alerts:
                self.last_alert_ids.add(new_alert["identifier"])
                self.hass.bus.async_fire("vma_new_alert", new_alert)
                _LOGGER.info("New VMA alert detected: %s", new_alert["identifier"])

            current_alert_ids = {alert["identifier"] for alert in active_alerts}
            self.last_alert_ids = self.last_alert_ids.intersection(current_alert_ids)

            latest_alert = active_alerts[0] if active_alerts else None

            _LOGGER.debug("Update completed. Latest alert: %s, Active alerts: %d", latest_alert["identifier"] if latest_alert else "None", len(active_alerts))

            return {
                "latest_alert": latest_alert,
                "active_alerts": active_alerts,
                "last_update": dt_util.utcnow()
            }
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to VMA API: %s", err)
            raise ConfigEntryNotReady(f"Error connecting to VMA API: {err}") from err

    async def _fetch_alerts(self, session: aiohttp.ClientSession, url: str) -> list:
        """Fetch alerts from a specific URL."""
        _LOGGER.debug("Fetching alerts from URL: %s", url)
        async with session.get(url) as response:
            if response.status != 200:
                _LOGGER.error("Error connecting to VMA API: %s", response.status)
                raise ConfigEntryNotReady(f"Error connecting to VMA API: {response.status}")
            data = await response.json()
        _LOGGER.debug("Fetched %d alerts", len(data.get("alerts", [])))
        return data.get("alerts", [])

    async def set_test_mode(self, test_mode: bool):
        """Set the test mode and refresh data."""
        _LOGGER.info("Setting VMA test mode to: %s", test_mode)
        self.test_mode = test_mode

        self.data = {"latest_alert": None, "active_alerts": [], "last_update": None}
        self.last_alert_ids.clear()

        _LOGGER.debug("Refreshing data after setting test mode")
        await self.async_refresh()
