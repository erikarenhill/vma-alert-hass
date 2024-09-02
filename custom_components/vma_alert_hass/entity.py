"""VMAEntity class for VMA Alert integration."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

class VMAEntity(CoordinatorEntity):
    """Base class for VMA entities."""

    def __init__(self, coordinator, config_entry):
        """Initialize the entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry

    @property
    def device_info(self):
        """Return device information about this VMA Alert device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="VMA Alert Device",
            manufacturer="Sveriges Radio",
            model="VMA Alert API",
            sw_version="2.0",
        )