"""API helpers for Home Ops Bridge."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_TOKEN,
    CONF_GROCY_URL,
    CONF_OPENPROJECT_URL,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)


async def _async_probe_endpoint(
    hass: HomeAssistant,
    url: str,
    *,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Probe one HTTP endpoint and return status details."""
    session = async_get_clientsession(hass)

    try:
        async with session.get(
            url,
            headers=headers,
            timeout=ClientTimeout(total=DEFAULT_REQUEST_TIMEOUT_SECONDS),
        ) as response:
            payload: dict[str, Any] | None = None
            if response.content_type == "application/json":
                payload = await response.json(content_type=None)

            return {
                "url": url,
                "reachable": response.status < 500,
                "status": response.status,
                "payload": payload,
                "error": None,
            }
    except (ClientError, TimeoutError) as err:
        return {
            "url": url,
            "reachable": False,
            "status": None,
            "payload": None,
            "error": str(err),
        }


async def async_probe_stack(hass: HomeAssistant, config: dict[str, Any]) -> dict[str, Any]:
    """Probe Grocy and OpenProject connectivity."""
    grocy_headers: dict[str, str] = {}

    api_token = config.get(CONF_API_TOKEN)
    if api_token:
        grocy_headers["GROCY-API-KEY"] = api_token

    grocy_base = config[CONF_GROCY_URL].rstrip("/") + "/"
    openproject_base = config[CONF_OPENPROJECT_URL].rstrip("/") + "/"

    grocy_status = await _async_probe_endpoint(
        hass,
        urljoin(grocy_base, "api/system/info"),
        headers=grocy_headers or None,
    )
    openproject_status = await _async_probe_endpoint(
        hass,
        urljoin(openproject_base, "api/v3"),
        headers=None,
    )

    return {
        "grocy": grocy_status,
        "openproject": openproject_status,
        "online": grocy_status["reachable"] and openproject_status["reachable"],
    }
