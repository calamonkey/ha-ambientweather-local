"""Diagnostics with host and identifiers redacted."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from . import AmbientLocalConfigEntry

REDACT = {CONF_HOST, "unique_id", "title", "mac_addr", "CurrTime"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AmbientLocalConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(dict(entry.data), REDACT),
        "options": dict(entry.options),
        "units": coordinator.units,
        "data": async_redact_data(coordinator.data, REDACT),
    }
