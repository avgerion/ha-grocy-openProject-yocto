"""Data coordinator for Home Ops Bridge."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.home_ops_bridge.api import async_probe_stack
from custom_components.home_ops_bridge.const import DEFAULT_SCAN_INTERVAL_SECONDS

LOGGER = logging.getLogger(__name__)


class HomeOpsBridgeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate stack status updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name="Home Ops Bridge",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self._entry = entry

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest status from Grocy and OpenProject endpoints."""
        config = {**self._entry.data, **self._entry.options}
        return await async_probe_stack(self.hass, config)
