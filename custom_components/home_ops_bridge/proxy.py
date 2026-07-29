"""HTTP proxy handlers for Grocy and OpenProject endpoints."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_GROCY_URL,
    CONF_OPENPROJECT_URL,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)

LOGGER = logging.getLogger(__name__)

# Headers to exclude when proxying requests (hop-by-hop headers)
EXCLUDE_HEADERS = {
    "host",
    "connection",
    "content-length",
    "transfer-encoding",
    "upgrade",
    "te",
    "trailers",
}


async def async_proxy_grocy(
    hass: HomeAssistant,
    config: dict[str, Any],
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> dict[str, Any]:
    """Proxy request to Grocy endpoint.
    
    Args:
        hass: Home Assistant instance
        config: Integration config dict with URLs
        method: HTTP method
        path: Request path (relative to grocy base)
        headers: Request headers
        body: Request body
    
    Returns:
        Response dict with status, headers, and body
    """
    grocy_url = config.get(CONF_GROCY_URL, "").rstrip("/")
    if not grocy_url:
        return {
            "status": 500,
            "error": "Grocy URL not configured",
        }

    return await _async_proxy_request(
        hass,
        grocy_url,
        method,
        path,
        "grocy",
        headers=headers,
        body=body,
    )


async def async_proxy_openproject(
    hass: HomeAssistant,
    config: dict[str, Any],
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> dict[str, Any]:
    """Proxy request to OpenProject endpoint.
    
    Args:
        hass: Home Assistant instance
        config: Integration config dict with URLs
        method: HTTP method
        path: Request path (relative to openproject base)
        headers: Request headers
        body: Request body
    
    Returns:
        Response dict with status, headers, and body
    """
    openproject_url = config.get(CONF_OPENPROJECT_URL, "").rstrip("/")
    if not openproject_url:
        return {
            "status": 500,
            "error": "OpenProject URL not configured",
        }

    return await _async_proxy_request(
        hass,
        openproject_url,
        method,
        path,
        "openproject",
        headers=headers,
        body=body,
    )


async def _async_proxy_request(
    hass: HomeAssistant,
    target_base_url: str,
    method: str,
    path: str,
    service_name: str,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> dict[str, Any]:
    """Proxy HTTP request to target service.
    
    Args:
        hass: Home Assistant instance
        target_base_url: Base URL of target service (e.g., http://localhost:9283)
        method: HTTP method (GET, POST, etc.)
        path: Request path
        service_name: Name of service for logging
        headers: Request headers
        body: Request body
    
    Returns:
        Response dict with status, headers, body, and optional error
    """
    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path

    # Build full target URL
    target_url = urljoin(target_base_url + "/", path.lstrip("/"))

    LOGGER.debug(
        "Proxying %s %s request to %s",
        method,
        service_name,
        target_url,
    )

    try:
        # Prepare headers for target request
        proxy_headers = _prepare_proxy_headers(headers or {})

        # Get HTTP session from Home Assistant
        session = async_get_clientsession(hass)

        # Forward request to target service
        async with session.request(
            method,
            target_url,
            headers=proxy_headers,
            data=body,
            timeout=ClientTimeout(total=DEFAULT_REQUEST_TIMEOUT_SECONDS),
            allow_redirects=True,
            ssl=False,  # Allow self-signed certs on local network
        ) as response:
            response_body = await response.read()

            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": response_body,
            }

    except asyncio.TimeoutError:
        LOGGER.warning(
            "%s proxy request timed out to %s",
            service_name,
            target_url,
        )
        return {
            "status": 504,
            "error": f"{service_name} service timeout",
        }
    except ClientError as err:
        LOGGER.error(
            "%s proxy request failed to %s: %s",
            service_name,
            target_url,
            err,
        )
        return {
            "status": 502,
            "error": f"Failed to connect to {service_name} service",
        }
    except Exception as err:
        LOGGER.exception(
            "Unexpected error proxying %s request to %s",
            service_name,
            target_url,
        )
        return {
            "status": 500,
            "error": "Internal proxy error",
        }


def _prepare_proxy_headers(headers: dict[str, str]) -> dict[str, str]:
    """Prepare headers for proxied request.
    
    Remove hop-by-hop headers and add necessary headers for target service.
    
    Args:
        headers: Original request headers
    
    Returns:
        Filtered headers suitable for proxying
    """
    proxy_headers = {}
    for key, value in headers.items():
        if key.lower() not in EXCLUDE_HEADERS:
            proxy_headers[key] = value

    # Add headers that indicate this is a proxy request
    # Note: In Home Assistant context, these may already be present
    if "user-agent" not in proxy_headers.lower():
        proxy_headers["User-Agent"] = "Home Assistant Home Ops Bridge/1.0"

    return proxy_headers
