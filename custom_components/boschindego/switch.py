"""Switch entities for Indego."""
import logging

from homeassistant.components.switch import (
    SwitchEntity,
    ENTITY_ID_FORMAT as SWITCH_ENTITY_ID_FORMAT,
)
from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .mixins import IndegoEntity
from .const import DATA_UPDATED, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        [
            entity
            for entity in hass.data[DOMAIN][config_entry.entry_id].entities.values()
            if isinstance(entity, IndegoSwitch)
        ]
    )


class IndegoSwitch(IndegoEntity, SwitchEntity):
    """Class for Indego Switches."""

    def __init__(
        self,
        entity_id: str,
        name: str,
        icon: str,
        device_info: DeviceInfo,
        indego_hub,
        translation_key: str = None,
        entity_category=None,
    ):
        """Initialize a switch.

        Args:
            entity_id (str): entity_id of the switch
            name (str): name of the switch
            icon (str): icon of the switch
            device_info (DeviceInfo): Initial device info
            indego_hub: Reference to the IndegoHub
            translation_key: Optional translation key for custom translations
            entity_category: Optional entity category for the switch
        """
        super().__init__(
            SWITCH_ENTITY_ID_FORMAT.format(entity_id), name, icon, None, device_info
        )

        self._indego_hub = indego_hub
        self._is_on = None
        self._attr_translation_key = translation_key
        self._attr_entity_category = entity_category

    async def async_added_to_hass(self):
        """Add switch to HASS."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()

        if state is not None and state.state is not None:
            if state.state == STATE_ON:
                self._is_on = True
            elif state.state == STATE_OFF:
                self._is_on = False

        async_dispatcher_connect(
            self.hass, DATA_UPDATED, self._schedule_immediate_update
        )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        # Check if SmartMowing is enabled by parsing the mowing mode description
        try:
            mowing_mode = getattr(
                self._indego_hub._indego_client.state, "mowing_mode_description", None
            )
            if mowing_mode:
                # Check if mowing mode contains "Smart" (SmartMowing indicator)
                self._is_on = "Smart" in str(mowing_mode)
            return self._is_on
        except (AttributeError, TypeError):
            return self._is_on

    @is_on.setter
    def is_on(self, value: bool):
        """Set is_on state."""
        if self._is_on != value:
            self._is_on = value
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on SmartMowing for mower %s", self._indego_hub.serial)
        await self._indego_hub._indego_client.put_mow_mode("true")
        await self._indego_hub._update_generic_data()
        self.is_on = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off SmartMowing for mower %s", self._indego_hub.serial)
        await self._indego_hub._indego_client.put_mow_mode("false")
        await self._indego_hub._update_generic_data()
        self.is_on = False

    @property
    def state(self) -> str:
        """Return the state of the switch."""
        if self.is_on is None:
            return STATE_UNKNOWN

        return STATE_ON if self.is_on else STATE_OFF
