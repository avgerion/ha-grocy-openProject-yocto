"""HTTP request handlers for web-based proxy endpoints."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.helpers.http import authenticated_middleware

from .const import DOMAIN
from .proxy import async_proxy_grocy, async_proxy_openproject

LOGGER = logging.getLogger(__name__)


async def async_register_web_handlers(hass: HomeAssistant) -> None:
    """Register web handlers for proxy endpoints.
    
    Endpoints:
    - /api/home_ops_bridge/grocy_proxy/* - Proxy to Grocy
    - /api/home_ops_bridge/openproject_proxy/* - Proxy to OpenProject
    """
    # This is typically handled by Home Assistant's HTTP component
    # We'll use webhook endpoints instead for better integration


async def async_setup_http_routes(app: web.Application, hass: HomeAssistant, entry_id: str) -> None:
    """Set up HTTP routes for proxy endpoints.
    
    Args:
        app: aiohttp application
        hass: Home Assistant instance  
        entry_id: Integration entry ID
    """
    config_entry = hass.config_entries.async_get_entry(entry_id)
    if not config_entry:
        LOGGER.error("Config entry %s not found", entry_id)
        return

    async def handle_grocy_proxy(request: web.Request) -> web.Response:
        """Handle Grocy proxy requests."""
        try:
            # Get config
            config = {**config_entry.data, **config_entry.options}

            # Extract relative path (remove /api/home_ops_bridge/grocy_proxy prefix)
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
                hass,
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

    async def handle_openproject_proxy(request: web.Request) -> web.Response:
        """Handle OpenProject proxy requests."""
        try:
            # Get config
            config = {**config_entry.data, **config_entry.options}

            # Extract relative path (remove /api/home_ops_bridge/openproject_proxy prefix)
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
                hass,
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

    # Register routes
    # Note: These routes should be registered with Home Assistant's web server
    # This would typically be done through the integration platform
    # For now, we'll document that iframes should use direct API calls to these endpoints
