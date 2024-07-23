"""The dyson integration."""

from __future__ import annotations

from libpurecool.dyson import DysonAccount

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .mock_device import Md

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations

# @dataclass
# class DysonData:
#    """Data from Dyson integration."""
#    coordinator_data: DysonDataUpdateCoordinator


# type DysonConfigEntry = ConfigEntry[DysonData]  # noqa: F821


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up dyson from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)
    da = DysonAccount("sven@rexkramer.de", "wgzvwquXHBTWEtwsfQwNy8pC", "DE")
    await hass.async_add_executor_job(da.login)
    dd = await hass.async_add_executor_job(da.devices)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = dd[0]
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
