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
        if self._attr_translation_key in (
            "security_enabled",
            "autolock",
            "automatic_update",
        ):
            return self._is_on

        try:
            mowing_mode = getattr(
                self._indego_hub._indego_client.generic_data,
                "mowing_mode_description",
                None,
            )

            if mowing_mode is not None:
                self._is_on = str(mowing_mode).lower() == "smartmowing"

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

        if self._attr_translation_key == "security_enabled":
            await self._indego_hub.async_set_security_enabled(True)
            self.is_on = True
            return

        if self._attr_translation_key == "autolock":
            await self._indego_hub.async_set_autolock(True)
            self.is_on = True
            return

        if self._attr_translation_key == "automatic_update":
            await self._indego_hub.async_set_automatic_update(True)
            self.is_on = True
            return

        self._indego_hub._forced_mowing_mode = "SmartMowing"

        await self._indego_hub._indego_client.put_mow_mode(True)

        self.is_on = True

        await self._indego_hub._update_predictive_calendar()
        await self._indego_hub._update_predictive_schedule()
        await self._indego_hub._update_calendar()
        await self._indego_hub._update_generic_data()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off SmartMowing for mower %s", self._indego_hub.serial)

        if self._attr_translation_key == "security_enabled":
            await self._indego_hub.async_set_security_enabled(False)
            self.is_on = False
            return

        if self._attr_translation_key == "autolock":
            await self._indego_hub.async_set_autolock(False)
            self.is_on = False
            return

        if self._attr_translation_key == "automatic_update":
            await self._indego_hub.async_set_automatic_update(False)
            self.is_on = False
            return

        self._indego_hub._forced_mowing_mode = "Calendar"

        await self._indego_hub._indego_client.put_mow_mode(False)

        await self._indego_hub.async_select_manual_calendar()

        self.is_on = False

        await self._indego_hub._update_predictive_calendar()
        await self._indego_hub._update_predictive_schedule()
        await self._indego_hub._update_calendar()
        await self._indego_hub._update_generic_data()

        mowing_mode = getattr(
            self._indego_hub._indego_client.generic_data,
            "mowing_mode_description",
            None,
        )

        if str(mowing_mode).lower() == "calendar":
            self._indego_hub._forced_mowing_mode = None

    @property
    def state(self) -> str:
        """Return the state of the switch."""
        if self.is_on is None:
            return STATE_UNKNOWN

        return STATE_ON if self.is_on else STATE_OFF
