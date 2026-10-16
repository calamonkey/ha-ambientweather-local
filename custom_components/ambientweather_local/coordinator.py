"""Data update coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AmbientLocalClient, CannotConnect
from .const import DEFAULT_UNIT_CODES, DOMAIN, UNITS_REFRESH_EVERY

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

    async def _async_update_data(self) -> dict[str, str | None]:
        try:
            if self._polls % UNITS_REFRESH_EVERY == 0:
                self.units = {**DEFAULT_UNIT_CODES, **await self.client.async_get_units()}
            self._polls += 1
            return await self.client.async_get_livedata()
        except CannotConnect as err:
            raise UpdateFailed(str(err)) from err
