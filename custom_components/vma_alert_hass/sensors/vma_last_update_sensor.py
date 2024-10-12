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
        self._attr_name = f"VMA Last Update - {coordinator.area_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.geo_code}_last_update"
        _LOGGER.debug("Initialized VMALastUpdateSensor for area: %s with unique_id: %s", coordinator.area_name, self._attr_unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        last_update = self.coordinator.data["last_update"]
        _LOGGER.debug("Last update for %s: %s", self._attr_name, last_update)
        return last_update.isoformat() if last_update else None

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
