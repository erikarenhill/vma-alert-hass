"""VMA Last Update sensor."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
import logging

from ..entity import VMAEntity
from ..coordinator import VMADataUpdateCoordinator
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VMALastUpdateSensor(VMAEntity, SensorEntity):
    """Representation of a VMA last update sensor."""

    def __init__(self, coordinator: VMADataUpdateCoordinator, config_entry: ConfigEntry):
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