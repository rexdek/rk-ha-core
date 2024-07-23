"""Dyson sensor."""

from dataclasses import dataclass
import logging

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DysonDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DysonSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Dyson switch entities."""


DYSON_SENSOR_TYPES: tuple[DysonSwitchEntityDescription, ...] = (
    DysonSwitchEntityDescription(
        key="Fan Power",
        device_class=SwitchDeviceClass,
        translation_key="air_quality",
        name="Fan Power",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the config entry for dyson sensor."""
    _LOGGER.debug("Instantiating DataUpdateCoordinator")
    coordinator = DysonDataUpdateCoordinator(
        hass,
        _LOGGER,
        hass.data[DOMAIN][entry.entry_id],
        name="Dyson Data Coordinator",
        update_interval=10,
    )
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(
        [DysonSwitch(coordinator, description) for description in DYSON_SENSOR_TYPES]
    )


class DysonSwitch(CoordinatorEntity, SwitchEntity):
    """Generich Zabbix Sensor."""

    entity_description: DysonSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, entity_description) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"dyson_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dyson.de",
            identifiers={(DOMAIN, "dyson.rexkramer.de")},
            manufacturer="Dyson",
            model=coordinator.dyson.name,
            name=coordinator.dyson.name,
            serial_number=coordinator.dyson.serial,
            sw_version=coordinator.dyson.version,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updating entity %s state", self.name)
        self._attr_native_value = self.coordinator.data
        self.async_write_ha_state()
