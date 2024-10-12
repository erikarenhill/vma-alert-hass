"""Config flow for VMA Alert integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_POLL_INTERVAL, SCB_GEO_CODES

_LOGGER = logging.getLogger(__name__)

def get_geo_code_options():
    """Get geo code options for the dropdown."""
    _LOGGER.debug("Generating geo code options for config flow")
    return {code: f"{code} - {name}" for code, name in SCB_GEO_CODES.items()}

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(
            "poll_interval",
            default=DEFAULT_POLL_INTERVAL,
            description="Polling interval in seconds for checking new alerts",
        ): vol.All(vol.Coerce(int), vol.Range(min=10)),
        vol.Required(
            "geo_code",
            default="00",
            description="SCB GeoCode for a specific region in Sweden",
        ): vol.In(get_geo_code_options()),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VMA Alert."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting config flow step_user with input: %s", user_input)
        if user_input is None:
            _LOGGER.debug("No user input, showing form")
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "default_interval": DEFAULT_POLL_INTERVAL,
                },
            )

        errors = {}

        try:
            self._validate_user_input(user_input)
        except ValueError as err:
            _LOGGER.error("Validation error: %s", err)
            errors["base"] = str(err)

        if errors:
            _LOGGER.debug("Validation errors found, reshowing form")
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
                description_placeholders={
                    "default_interval": DEFAULT_POLL_INTERVAL,
                },
            )

        title = f"VMA Alert - {SCB_GEO_CODES[user_input['geo_code']]}"
        _LOGGER.debug("Config flow completed successfully, creating entry with title: %s", title)
        return self.async_create_entry(title=title, data=user_input)

    def _validate_user_input(self, user_input: dict[str, Any]) -> None:
        """Validate the user input."""
        _LOGGER.debug("Validating user input: %s", user_input)
        poll_interval = user_input.get("poll_interval")
        if poll_interval is not None and poll_interval < 10:
            raise ValueError("Poll interval must be at least 10 seconds.")

        geo_code = user_input.get("geo_code")
        if geo_code not in SCB_GEO_CODES:
            raise ValueError(f"Invalid geo code: {geo_code}")
        _LOGGER.debug("User input validation successful")
