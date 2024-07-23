"""Dyson Data Update Coordinator."""

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DysonDataUpdateCoordinator(DataUpdateCoordinator):
    """class to manage fetching data from Dyson."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        dyson,
        name: str = DOMAIN,
        update_interval: int = 30,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=datetime.timedelta(seconds=update_interval),
        )
        self.dyson = dyson

    async def _async_update_data(self):
        """Retrieve value."""
        # return next(self.dyson.result())
        await self.hass.async_add_executor_job(self.dyson.connect, "dyson.rexkramer.de")
        state = self.dyson.state
        await self.hass.async_add_executor_job(self.dyson.disconnect)
        print(state)
        return state.fan_power
