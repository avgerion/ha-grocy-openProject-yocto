"""Sensor platform for Home Ops Bridge."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.home_ops_bridge.const import DOMAIN
from custom_components.home_ops_bridge.coordinator import HomeOpsBridgeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Home Ops Bridge sensors from a config entry."""
    coordinator: HomeOpsBridgeCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            HomeOpsBridgeEndpointStatusSensor(entry, coordinator, "grocy"),
            HomeOpsBridgeEndpointStatusSensor(entry, coordinator, "openproject"),
            HomeOpsBridgeOverallStatusSensor(entry, coordinator),
        ]
    )


class HomeOpsBridgeBaseSensor(CoordinatorEntity[HomeOpsBridgeCoordinator], SensorEntity):
    """Base class for Home Ops Bridge sensors."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, coordinator: HomeOpsBridgeCoordinator) -> None:
        """Initialize base sensor."""
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return shared device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Home Ops Bridge",
            manufacturer="Community",
            model="Yocto Grocy/OpenProject Bridge",
        )


class HomeOpsBridgeEndpointStatusSensor(HomeOpsBridgeBaseSensor):
    """Connectivity sensor for one endpoint."""

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: HomeOpsBridgeCoordinator,
        endpoint_key: str,
    ) -> None:
        """Initialize endpoint sensor."""
        super().__init__(entry, coordinator)
        self._endpoint_key = endpoint_key
        self._attr_name = f"Home Ops Bridge {endpoint_key.title()}"
        self._attr_unique_id = f"{entry.entry_id}_{endpoint_key}_status"

    @property
    def native_value(self) -> str:
        """Return sensor state."""
        endpoint = self.coordinator.data.get(self._endpoint_key, {}) if self.coordinator.data else {}
        return "online" if endpoint.get("reachable") else "offline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for diagnostics."""
        endpoint = self.coordinator.data.get(self._endpoint_key, {}) if self.coordinator.data else {}
        payload = endpoint.get("payload") or {}

        attrs: dict[str, Any] = {
            "url": endpoint.get("url"),
            "status": endpoint.get("status"),
            "error": endpoint.get("error"),
        }

        version = payload.get("version") if isinstance(payload, dict) else None
        if version:
            attrs["version"] = version

        return attrs


class HomeOpsBridgeOverallStatusSensor(HomeOpsBridgeBaseSensor):
    """Overall bridge status sensor."""

    _attr_name = "Home Ops Bridge Overall"

    def __init__(self, entry: ConfigEntry, coordinator: HomeOpsBridgeCoordinator) -> None:
        """Initialize overall sensor."""
        super().__init__(entry, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_overall_status"

    @property
    def native_value(self) -> str:
        """Return online/offline for the full stack."""
        if not self.coordinator.data:
            return "offline"
        return "online" if self.coordinator.data.get("online") else "offline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return combined diagnostics."""
        if not self.coordinator.data:
            return {}

        return {
            "grocy_reachable": self.coordinator.data.get("grocy", {}).get("reachable"),
            "openproject_reachable": self.coordinator.data.get("openproject", {}).get("reachable"),
        }
