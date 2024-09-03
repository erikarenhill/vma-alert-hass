"""Sensor platform for VMA Alert integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensors.vma_sensor import VMASensor
from .sensors.vma_count_sensor import VMACountSensor
from .sensors.vma_last_update_sensor import VMALastUpdateSensor

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VMA Alert sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        VMASensor(coordinator, config_entry),
        VMACountSensor(coordinator, config_entry),
        VMALastUpdateSensor(coordinator, config_entry),
    ], True)