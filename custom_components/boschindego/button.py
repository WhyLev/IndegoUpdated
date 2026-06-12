from __future__ import annotations
import logging

from homeassistant.components.button import (
    ButtonEntity,
    ENTITY_ID_FORMAT as BUTTON_ENTITY_ID_FORMAT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MOWER_SERIAL, DOMAIN
from .mixins import IndegoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    async_add_entities(
        [
            entity
            for entity in hass.data[DOMAIN][config_entry.entry_id].entities.values()
            if isinstance(entity, IndegoAlertButton)
        ]
    )


class IndegoAlertButton(IndegoEntity, ButtonEntity):
    """Button entity for alert actions."""

    def __init__(
        self,
        entity_id: str,
        name: str | None,
        icon: str | None,
        service_name: str,
        service_data: dict | None,
        device_info,
        indego_hub,
        translation_key: str | None = None,
        entity_category=None,
    ) -> None:
        super().__init__(
            BUTTON_ENTITY_ID_FORMAT.format(entity_id),
            name,
            icon,
            None,
            device_info,
        )
        self._indego_hub = indego_hub
        self._service_name = service_name
        self._service_data = service_data or {}
        self._attr_translation_key = translation_key
        self._attr_entity_category = entity_category

    async def async_press(self) -> None:
        """Handle button press."""
        service_data = {
            CONF_MOWER_SERIAL: self._indego_hub.serial,
            **self._service_data,
        }
        _LOGGER.info(
            "Executing service %s for mower %s with data %s",
            self._service_name,
            self._indego_hub.serial,
            service_data,
        )
        await self.hass.services.async_call(
            DOMAIN, self._service_name, service_data, blocking=True
        )