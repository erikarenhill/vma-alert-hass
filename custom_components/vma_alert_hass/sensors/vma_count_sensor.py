"""VMA Count sensor."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
import logging

from ..entity import VMAEntity
from ..coordinator import VMADataUpdateCoordinator
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VMACountSensor(VMAEntity, SensorEntity):
    """Representation of a VMA count sensor."""

    def __init__(self, coordinator: VMADataUpdateCoordinator, config_entry: ConfigEntry):
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