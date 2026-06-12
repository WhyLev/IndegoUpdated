"""Diagnostics for Indego integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Data to redact from diagnostics
TO_REDACT = {
    CONF_TOKEN: "TOKEN",
    "access_token": "TOKEN",
    "refresh_token": "TOKEN",
    "id_token": "TOKEN",
    "scope": ["SCOPE"],
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    from .const import (
        ENTITY_ONLINE,
        CONF_MOWER_SERIAL,
        CONF_MOWER_NAME,
        CONF_EXPOSE_INDEGO_AS_MOWER,
        CONF_EXPOSE_INDEGO_AS_VACUUM,
        CONF_SHOW_ALL_ALERTS,
        CONF_USER_AGENT,
    )

    hub = hass.data[DOMAIN].get(entry.entry_id)
    if not hub:
        return {"error": "Integration not loaded"}

    # Get mower online status
    online_entity = hub.entities.get(ENTITY_ONLINE)
    is_online = online_entity.state if online_entity else None

    # Calculate last API response time (in seconds ago)
    last_response_ago = None
    if hub._last_successful_update:
        import time
        last_response_ago = round(time.time() - hub._last_successful_update, 1)

    config_data = async_redact_data(entry.data, TO_REDACT)
    options_data = async_redact_data(entry.options, TO_REDACT)

    return {
        "config": {
            CONF_MOWER_NAME: entry.data.get(CONF_MOWER_NAME),
            CONF_MOWER_SERIAL: f"{entry.data.get(CONF_MOWER_SERIAL, '')[:4]}****"
            if entry.data.get(CONF_MOWER_SERIAL)
            else None,
            "options": {
                CONF_EXPOSE_INDEGO_AS_MOWER: entry.options.get(
                    CONF_EXPOSE_INDEGO_AS_MOWER, False
                ),
                CONF_EXPOSE_INDEGO_AS_VACUUM: entry.options.get(
                    CONF_EXPOSE_INDEGO_AS_VACUUM, False
                ),
                CONF_SHOW_ALL_ALERTS: entry.options.get(CONF_SHOW_ALL_ALERTS, False),
                CONF_USER_AGENT: f"[{'custom' if options_data.get(CONF_USER_AGENT) else 'default'}]",
            },
        },
        "connection_metrics": {
            "mower_online": is_online,
            "last_successful_update_seconds_ago": last_response_ago,
            "last_service_error": hub._last_service_error,
            "consecutive_timeouts": hub._consecutive_timeouts,
            "online_timeout_threshold_seconds": 300,
        },
        "session_tracking": {
            "total_mowing_sessions": hub._session_count,
        },
        "error_tracking": {
            "last_error_code": hub._last_error_code,
            "last_error_time": (
                hub._last_error_time.isoformat() if hub._last_error_time else None
            ),
        },
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    from .const import (
        ENTITY_BATTERY,
        ENTITY_BATTERY_VOLTAGE,
        ENTITY_BATTERY_DISCHARGE,
        ENTITY_BATTERY_CYCLES,
        ENTITY_BATTERY_TEMPERATURE,
        ENTITY_AMBIENT_TEMPERATURE,
        ENTITY_GARDEN_SIZE,
        ENTITY_RUNTIME,
        ENTITY_MOWER_STATE,
        ENTITY_ALERT,
        ENTITY_MOWER_STUCK,
        ENTITY_FIRMWARE_VERSION,
        ENTITY_MAINTENANCE_HOURS,
        ENTITY_SESSION_COUNT,
        ENTITY_LAST_ERROR_CODE,
        ENTITY_MOWING_MODE,
    )

    hub = hass.data[DOMAIN].get(entry.entry_id)
    if not hub:
        return {"error": "Integration not loaded"}

    try:
        state = hub._indego_client.state
        generic_data = hub._indego_client.generic_data
        operating_data = hub._indego_client.operating_data
        alerts = hub._indego_client.alerts

        # Build mower state info
        mower_state_entity = hub.entities.get(ENTITY_MOWER_STATE)
        mower_state = mower_state_entity.state if mower_state_entity else None

        # Build battery info
        battery_entity = hub.entities.get(ENTITY_BATTERY)
        battery_pct = battery_entity.state if battery_entity else None

        battery_voltage_entity = hub.entities.get(ENTITY_BATTERY_VOLTAGE)
        battery_voltage = battery_voltage_entity.state if battery_voltage_entity else None

        battery_temp_entity = hub.entities.get(ENTITY_BATTERY_TEMPERATURE)
        battery_temp = battery_temp_entity.state if battery_temp_entity else None

        ambient_temp_entity = hub.entities.get(ENTITY_AMBIENT_TEMPERATURE)
        ambient_temp = ambient_temp_entity.state if ambient_temp_entity else None

        # Build garden size
        garden_size_entity = hub.entities.get(ENTITY_GARDEN_SIZE)
        garden_size = garden_size_entity.state if garden_size_entity else None

        # Build runtime info
        runtime_entity = hub.entities.get(ENTITY_RUNTIME)
        total_cut_hours = runtime_entity.state if runtime_entity else None

        # Build alert info
        alert_entity = hub.entities.get(ENTITY_ALERT)
        unread_alert_count = sum(
            1 for alert in alerts if not alert.read_status
        ) if alerts else 0

        # Build stuck info
        stuck_entity = hub.entities.get(ENTITY_MOWER_STUCK)
        is_stuck = stuck_entity.state if stuck_entity else False

        # Build maintenance hours
        maintenance_entity = hub.entities.get(ENTITY_MAINTENANCE_HOURS)
        maintenance_hours = maintenance_entity.state if maintenance_entity else None

        # Build session count
        session_entity = hub.entities.get(ENTITY_SESSION_COUNT)
        session_count = session_entity.state if session_entity else None

        # Build last error code
        error_code_entity = hub.entities.get(ENTITY_LAST_ERROR_CODE)
        last_error_code = error_code_entity.state if error_code_entity else None

        # Build mowing mode
        mowing_mode_entity = hub.entities.get(ENTITY_MOWING_MODE)
        mowing_mode = mowing_mode_entity.state if mowing_mode_entity else None

        # Build firmware version
        firmware_entity = hub.entities.get(ENTITY_FIRMWARE_VERSION)
        firmware_version = firmware_entity.state if firmware_entity else None

        diagnostics: dict[str, Any] = {
            "device_info": {
                "manufacturer": "Bosch",
                "model": generic_data.bareToolnumber if generic_data else None,
                "firmware_version": firmware_version,
                "mower_name": hub._mower_name,
            },
            "mower_state": {
                "state_description": mower_state,
                "state_code": state.state if state else None,
                "mowed_percentage": state.mowed if state else None,
                "is_stuck": is_stuck,
                "position": "[REDACTED]",  # Redact coordinates for privacy
            },
            "battery": {
                "percentage": battery_pct,
                "voltage_v": battery_voltage,
                "temperature_c": battery_temp,
                "ambient_temperature_c": ambient_temp,
                "charging": hub.entities[ENTITY_BATTERY].charging
                if ENTITY_BATTERY in hub.entities
                else False,
            },
            "garden": {
                "size_m2": garden_size,
            },
            "runtime": {
                "total_mowing_hours": total_cut_hours,
            },
            "alerts": {
                "total_count": len(alerts) if alerts else 0,
                "unread_count": unread_alert_count,
            },
            "tracking": {
                "total_sessions": session_count,
                "maintenance_hours": maintenance_hours,
                "mowing_mode": mowing_mode,
                "last_error_code": last_error_code,
            },
        }

        return diagnostics

    except Exception as err:
        _LOGGER.warning("Error gathering device diagnostics: %s", err)
        return {"error": f"Failed to gather diagnostics: {str(err)}"}
