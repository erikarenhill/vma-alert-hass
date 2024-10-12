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
        self._attr_name = f"Active VMA Alerts - {coordinator.area_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.geo_code}_active_alert_count"
        _LOGGER.debug("Initialized VMACountSensor for area: %s with unique_id: %s", coordinator.area_name, self._attr_unique_id)

    @property
    def state(self):
        """Return the number of active VMA alerts."""
        count = len(self.coordinator.data["active_alerts"])
        _LOGGER.debug("Active alert count for %s: %d", self._attr_name, count)
        return count

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
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
        _LOGGER.debug("Extra state attributes for %s: %s", self._attr_name, attributes)
        return attributes
