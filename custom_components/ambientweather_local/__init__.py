"""AmbientWeather Local: read an AmbientWeather station directly over the LAN."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmbientLocalClient
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .coordinator import AmbientLocalCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

type AmbientLocalConfigEntry = ConfigEntry[AmbientLocalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AmbientLocalConfigEntry) -> bool:
    client = AmbientLocalClient(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = AmbientLocalCoordinator(
        hass,
        client,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        entry.unique_id or entry.data[CONF_HOST],
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass: HomeAssistant, entry: AmbientLocalConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: AmbientLocalConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
