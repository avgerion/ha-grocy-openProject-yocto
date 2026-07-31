"""Home Ops Bridge integration."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback

from .coordinator import HomeOpsBridgeCoordinator
from .const import DOMAIN
from .proxy import async_proxy_grocy, async_proxy_openproject

LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]

SERVICE_GROCY_PROXY = "grocy_proxy"
SERVICE_OPENPROJECT_PROXY = "openproject_proxy"


class GrocyProxyView(HomeAssistantView):
    """Handle Grocy proxy requests."""

    url = "/api/home_ops_bridge/grocy_proxy{path_info:.*}"
    name = "api:home_ops_bridge:grocy_proxy"
    requires_auth = True

    def __init__(self, config_entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the view."""
        super().__init__()
        self.config_entry = config_entry
        self.hass = hass

    async def _handle_proxy(self, request: web.Request) -> web.Response:
        """Handle proxy request."""
        try:
            config = {**self.config_entry.data, **self.config_entry.options}

            # Extract relative path
            path = request.path
            prefix = "/api/home_ops_bridge/grocy_proxy"
            if path.startswith(prefix):
                relative_path = path[len(prefix) :]
            else:
                relative_path = "/"

            # Add query string
            if request.query_string:
                relative_path += f"?{request.query_string}"

            # Get request body
            body = None
            if request.content_length and request.content_length > 0:
                body = await request.read()

            # Proxy request
            result = await async_proxy_grocy(
                self.hass,
                config,
                request.method,
                relative_path,
                headers=dict(request.headers),
                body=body,
            )

            # Handle error responses
            if "error" in result:
                return web.json_response(
                    {"error": result["error"]},
                    status=result.get("status", 500),
                )

            # Return proxied response
            response = web.StreamResponse(
                status=result.get("status", 200),
                headers=result.get("headers", {}),
            )
            response.body = result.get("body", b"")
            return response

        except Exception as err:
            LOGGER.exception("Error handling Grocy proxy request")
            return web.json_response(
                {"error": "Internal proxy error"},
                status=500,
            )

    async def get(self, request: web.Request) -> web.Response:
        """Handle GET request."""
        return await self._handle_proxy(request)

    async def post(self, request: web.Request) -> web.Response:
        """Handle POST request."""
        return await self._handle_proxy(request)

    async def put(self, request: web.Request) -> web.Response:
        """Handle PUT request."""
        return await self._handle_proxy(request)

    async def delete(self, request: web.Request) -> web.Response:
        """Handle DELETE request."""
        return await self._handle_proxy(request)

    async def patch(self, request: web.Request) -> web.Response:
        """Handle PATCH request."""
        return await self._handle_proxy(request)


class OpenProjectProxyView(HomeAssistantView):
    """Handle OpenProject proxy requests."""

    url = "/api/home_ops_bridge/openproject_proxy{path_info:.*}"
    name = "api:home_ops_bridge:openproject_proxy"
    requires_auth = True

    def __init__(self, config_entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the view."""
        super().__init__()
        self.config_entry = config_entry
        self.hass = hass

    async def _handle_proxy(self, request: web.Request) -> web.Response:
        """Handle proxy request."""
        try:
            config = {**self.config_entry.data, **self.config_entry.options}

            # Extract relative path
            path = request.path
            prefix = "/api/home_ops_bridge/openproject_proxy"
            if path.startswith(prefix):
                relative_path = path[len(prefix) :]
            else:
                relative_path = "/"

            # Add query string
            if request.query_string:
                relative_path += f"?{request.query_string}"

            # Get request body
            body = None
            if request.content_length and request.content_length > 0:
                body = await request.read()

            # Proxy request
            result = await async_proxy_openproject(
                self.hass,
                config,
                request.method,
                relative_path,
                headers=dict(request.headers),
                body=body,
            )

            # Handle error responses
            if "error" in result:
                return web.json_response(
                    {"error": result["error"]},
                    status=result.get("status", 500),
                )

            # Return proxied response
            response = web.StreamResponse(
                status=result.get("status", 200),
                headers=result.get("headers", {}),
            )
            response.body = result.get("body", b"")
            return response

        except Exception as err:
            LOGGER.exception("Error handling OpenProject proxy request")
            return web.json_response(
                {"error": "Internal proxy error"},
                status=500,
            )

    async def get(self, request: web.Request) -> web.Response:
        """Handle GET request."""
        return await self._handle_proxy(request)

    async def post(self, request: web.Request) -> web.Response:
        """Handle POST request."""
        return await self._handle_proxy(request)

    async def put(self, request: web.Request) -> web.Response:
        """Handle PUT request."""
        return await self._handle_proxy(request)

    async def delete(self, request: web.Request) -> web.Response:
        """Handle DELETE request."""
        return await self._handle_proxy(request)

    async def patch(self, request: web.Request) -> web.Response:
        """Handle PATCH request."""
        return await self._handle_proxy(request)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Ops Bridge from a config entry."""
    coordinator = HomeOpsBridgeCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
    }

    # Register proxy services
    async def handle_grocy_proxy(call) -> dict[str, Any]:
        """Handle Grocy proxy service call."""
        config = {**entry.data, **entry.options}
        return await async_proxy_grocy(
            hass,
            config,
            call.data.get("method", "GET"),
            call.data.get("path", "/"),
            headers=call.data.get("headers"),
            body=call.data.get("body"),
        )

    async def handle_openproject_proxy(call) -> dict[str, Any]:
        """Handle OpenProject proxy service call."""
        config = {**entry.data, **entry.options}
        return await async_proxy_openproject(
            hass,
            config,
            call.data.get("method", "GET"),
            call.data.get("path", "/"),
            headers=call.data.get("headers"),
            body=call.data.get("body"),
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GROCY_PROXY,
        handle_grocy_proxy,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_OPENPROJECT_PROXY,
        handle_openproject_proxy,
        schema=None,
    )

    # Register HTTP views for proxy endpoints
    hass.http.register_view(GrocyProxyView(entry, hass))
    hass.http.register_view(OpenProjectProxyView(entry, hass))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

        # Unregister services
        hass.services.async_remove(DOMAIN, SERVICE_GROCY_PROXY)
        hass.services.async_remove(DOMAIN, SERVICE_OPENPROJECT_PROXY)

    return unload_ok
