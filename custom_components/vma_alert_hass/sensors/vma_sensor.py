"""VMA Alert sensor."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
import logging

from ..entity import VMAEntity
from ..coordinator import VMADataUpdateCoordinator
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VMASensor(VMAEntity, SensorEntity):
    """Representation of a VMA sensor."""

    def __init__(self, coordinator: VMADataUpdateCoordinator, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"VMA Alert - {coordinator.area_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.geo_code}_latest_alert"
        _LOGGER.debug("Initialized VMASensor for area: %s with unique_id: %s", coordinator.area_name, self._attr_unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        latest_alert = self.coordinator.data["latest_alert"]

        _LOGGER.debug("Latest alert data for %s: %s", self._attr_name, latest_alert)
        
        return latest_alert["identifier"] if latest_alert else "No active alerts"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        latest_alert = self.coordinator.data["latest_alert"]
        if latest_alert:
            attributes = {
                "sent": latest_alert["sent"],
                "description": latest_alert["info"][0]["description"],
                "area": latest_alert["info"][0]["area"][0]["areaDesc"],
            }
            _LOGGER.debug("Extra state attributes for %s: %s", self._attr_name, attributes)
            return attributes
        _LOGGER.debug("No extra state attributes for %s (no active alerts)", self._attr_name)
        return {}
