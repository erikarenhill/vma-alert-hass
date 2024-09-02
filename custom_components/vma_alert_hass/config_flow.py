"""Config flow for VMA Alert integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_POLL_INTERVAL

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(
            "poll_interval",
            default=DEFAULT_POLL_INTERVAL,
            description="Polling interval in seconds for checking new alerts",
        ): int,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VMA Alert."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "default_interval": DEFAULT_POLL_INTERVAL,
                },
            )

        return self.async_create_entry(title="VMA Alert", data=user_input)