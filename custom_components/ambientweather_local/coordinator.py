"""Data update coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AmbientLocalClient, CannotConnect
from .const import (
    DEFAULT_UNIT_CODES,
    DOMAIN,
    MAX_TOLERATED_FAILURES,
    UNITS_REFRESH_EVERY,
)

_LOGGER = logging.getLogger(__name__)


class AmbientLocalCoordinator(DataUpdateCoordinator[dict[str, str | None]]):
    """Poll livedata.htm (and occasionally station.htm for units)."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AmbientLocalClient,
        interval: int,
        unique_id: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.client = client
        self.unique_id = unique_id
        self.units: dict[str, str] = dict(DEFAULT_UNIT_CODES)
        self._polls = 0
        self._failures = 0

    async def _async_update_data(self) -> dict[str, str | None]:
        if self._polls % UNITS_REFRESH_EVERY == 0:
            try:
                self.units = {**self.units, **await self.client.async_get_units()}
            except CannotConnect as err:
                # Units rarely change; keep the cached ones and carry on.
                _LOGGER.debug("Could not refresh station units: %s", err)
        self._polls += 1
        try:
            data = await self.client.async_get_livedata()
        except CannotConnect as err:
            self._failures += 1
            if self.data is not None and self._failures < MAX_TOLERATED_FAILURES:
                # Brief hiccup: keep the last values instead of going unknown.
                _LOGGER.debug("Poll failed (%s), keeping previous data", err)
                return self.data
            raise UpdateFailed(str(err)) from err
        self._failures = 0
        return data
