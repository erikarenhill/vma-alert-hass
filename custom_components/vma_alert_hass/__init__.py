"""The VMA Alert integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError

from .const import DOMAIN
from .coordinator import VMADataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the VMA Alert component."""
    _LOGGER.debug("Setting up VMA Alert component")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VMA Alert from a config entry."""
    _LOGGER.debug("Setting up VMA Alert integration for entry: %s", entry.entry_id)
    
    try:
        poll_interval = entry.data["poll_interval"]
        geo_code = entry.data.get("geo_code")
    except KeyError as err:
        _LOGGER.error("Missing required configuration: %s", err)
        raise ConfigEntryNotReady(f"Missing required configuration: {err}") from err
    
    _LOGGER.debug(f"Creating VMADataUpdateCoordinator with poll_interval: {poll_interval}, geo_code: {geo_code}")
    
    try:
        coordinator = VMADataUpdateCoordinator(hass, poll_interval, geo_code)
    except Exception as err:
        _LOGGER.error("Failed to create VMADataUpdateCoordinator: %s", err)
        raise ConfigEntryNotReady(f"Failed to create VMADataUpdateCoordinator: {err}") from err

    try:
        _LOGGER.debug("Attempting first refresh of coordinator")
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady as err:
        _LOGGER.error(f"Failed to load VMA Alert integration: ConfigEntryNotReady - {err}")
        raise
    except Exception as err:
        _LOGGER.error(f"Unexpected error during VMA Alert setup: {err}", exc_info=True)
        raise ConfigEntryNotReady(f"Unexpected error: {err}")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.debug("VMA Alert integration setup completed for entry: %s", entry.entry_id)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading VMA Alert integration for entry: %s", entry.entry_id)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    _LOGGER.debug("VMA Alert integration unloaded: %s", unload_ok)
    return unload_ok
