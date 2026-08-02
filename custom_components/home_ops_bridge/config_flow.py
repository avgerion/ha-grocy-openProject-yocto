"""Config flow for Home Ops Bridge."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.core import callback

from .api import async_probe_stack
from .const import (
    CONF_API_TOKEN,
    CONF_GROCY_URL,
    CONF_OPENPROJECT_URL,
    DEFAULT_GROCY_PORT,
    DEFAULT_OPENPROJECT_PORT,
    DOMAIN,
)


def _normalize_url(url: str) -> str:
    """Normalize user-provided URL input."""
    cleaned = url.strip()
    if "://" not in cleaned:
        cleaned = f"http://{cleaned}"

    parsed = urlparse(cleaned)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


class HomeOpsBridgeConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Home Ops Bridge."""

    domain = DOMAIN
    VERSION = 1
    _discovered_input: dict[str, str] | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return HomeOpsBridgeOptionsFlow(config_entry)

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        """Handle zeroconf discovery."""
        host = discovery_info.host
        self._discovered_input = {
            CONF_GROCY_URL: f"http://{host}:{DEFAULT_GROCY_PORT}",
            CONF_OPENPROJECT_URL: f"http://{host}:{DEFAULT_OPENPROJECT_PORT}",
            CONF_API_TOKEN: "",
        }
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        candidate_input = user_input or self._discovered_input or {}

        if user_input is not None:
            try:
                normalized = {
                    CONF_GROCY_URL: _normalize_url(user_input[CONF_GROCY_URL]),
                    CONF_OPENPROJECT_URL: _normalize_url(user_input[CONF_OPENPROJECT_URL]),
                    CONF_API_TOKEN: user_input.get(CONF_API_TOKEN, "").strip(),
                }
            except ValueError:
                errors["base"] = "invalid_url"
                normalized = user_input

            if not errors:
                status = await async_probe_stack(self.hass, normalized)
                if status["online"]:
                    await self.async_set_unique_id(
                        f"{normalized[CONF_GROCY_URL]}|{normalized[CONF_OPENPROJECT_URL]}"
                    )
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title="Home Ops Bridge", data=normalized)

                errors["base"] = "cannot_connect"

            candidate_input = normalized

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GROCY_URL,
                    default=candidate_input.get(
                        CONF_GROCY_URL,
                        f"http://raspberrypi.local:{DEFAULT_GROCY_PORT}",
                    ),
                ): str,
                vol.Required(
                    CONF_OPENPROJECT_URL,
                    default=candidate_input.get(
                        CONF_OPENPROJECT_URL,
                        f"http://raspberrypi.local:{DEFAULT_OPENPROJECT_PORT}",
                    ),
                ): str,
                vol.Optional(
                    CONF_API_TOKEN,
                    default=candidate_input.get(CONF_API_TOKEN, ""),
                ): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class HomeOpsBridgeOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Home Ops Bridge."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage integration options."""
        if user_input is not None:
            normalized = {
                CONF_GROCY_URL: _normalize_url(user_input[CONF_GROCY_URL]),
                CONF_OPENPROJECT_URL: _normalize_url(user_input[CONF_OPENPROJECT_URL]),
                CONF_API_TOKEN: user_input.get(CONF_API_TOKEN, "").strip(),
            }
            return self.async_create_entry(title="", data=normalized)

        current_data = {**self.config_entry.data, **self.config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GROCY_URL,
                    default=current_data.get(CONF_GROCY_URL, ""),
                ): str,
                vol.Required(
                    CONF_OPENPROJECT_URL,
                    default=current_data.get(CONF_OPENPROJECT_URL, ""),
                ): str,
                vol.Optional(
                    CONF_API_TOKEN,
                    default=current_data.get(CONF_API_TOKEN, ""),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
