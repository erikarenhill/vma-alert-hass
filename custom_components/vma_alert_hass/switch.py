"""Switch platform for VMA Alert integration."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VMAEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VMA Alert switch."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VMATestModeSwitch(coordinator, config_entry)], True)

class VMATestModeSwitch(VMAEntity, SwitchEntity):
    """Representation of a VMA Test Mode switch."""

    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"VMA Test Mode - {coordinator.area_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.geo_code}_test_mode"
        _LOGGER.debug("Initialized VMATestModeSwitch for area: %s with unique_id: %s", coordinator.area_name, self._attr_unique_id)

    @property
    def is_on(self):
        """Return true if test mode is on."""
        return self.coordinator.test_mode

    async def async_turn_on(self, **kwargs):
        """Turn on test mode."""
        _LOGGER.debug("Turning on VMA Test Mode for %s", self._attr_name)
        await self.coordinator.set_test_mode(True)

    async def async_turn_off(self, **kwargs):
        """Turn off test mode."""
        _LOGGER.debug("Turning off VMA Test Mode for %s", self._attr_name)
        await self.coordinator.set_test_mode(False)
