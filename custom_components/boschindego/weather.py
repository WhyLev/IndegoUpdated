"""Weather entity for Indego predictive weather."""
from datetime import datetime, timezone
import logging

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPrecipitationDepth,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
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
    """Set up the weather platform."""
    async_add_entities(
        [
            entity
            for entity in hass.data[DOMAIN][config_entry.entry_id].entities.values()
            if isinstance(entity, IndegoWeather)
        ]
    )


def _weather_condition(symbol) -> str:
    """Map Bosch weather symbol to Home Assistant weather condition."""
    symbol = str(symbol or "")

    mapping = {
        "100000": "sunny",
        "110000": "partlycloudy",
        "111000": "rainy",
        "120000": "partlycloudy",
        "121000": "rainy",
        "200000": "cloudy",
        "210000": "cloudy",
        "211000": "rainy",
        "221000": "pouring",
    }

    if symbol in mapping:
        return mapping[symbol]

    if symbol.startswith("1"):
        return "partlycloudy"

    if symbol.startswith("2"):
        return "cloudy"

    return "partlycloudy"


def _forecast_intervals(weather_data) -> list:
    """Return forecast intervals from Bosch predictive weather response."""
    try:
        return (
            weather_data
            .get("LocationWeather", {})
            .get("forecast", {})
            .get("intervals", [])
        )
    except AttributeError:
        return []


def _parse_datetime(value):
    """Parse Bosch UTC datetime string."""
    if not value:
        return None

    return datetime.fromisoformat(
        str(value).replace("Z", "+00:00")
    )


class IndegoWeather(IndegoEntity, WeatherEntity):
    """Indego predictive weather entity."""

    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY
        | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(
        self,
        entity_id: str,
        name: str,
        device_info: DeviceInfo,
        indego_hub,
        translation_key: str = None,
        entity_category=None,
    ):
        """Initialize Indego weather entity."""
        super().__init__(
            f"weather.{entity_id}",
            name,
            "mdi:weather-partly-cloudy",
            None,
            device_info,
        )

        self._indego_hub = indego_hub
        self._weather_data = None
        self._attr_translation_key = translation_key
        self._attr_entity_category = entity_category
        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS

    async def async_added_to_hass(self):
        """Add weather entity to HASS."""
        await super().async_added_to_hass()

        async_dispatcher_connect(
            self.hass,
            DATA_UPDATED,
            self._schedule_immediate_update,
        )

    @property
    def weather_data(self):
        """Return raw weather data."""
        return self._weather_data

    @weather_data.setter
    def weather_data(self, value):
        """Set raw weather data."""
        self._weather_data = value
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if weather data is available."""
        return bool(_forecast_intervals(self._weather_data))

    @property
    def native_temperature(self):
        """Return current temperature."""
        intervals = _forecast_intervals(self._weather_data)

        if not intervals:
            return None

        return intervals[0].get("tt")

    @property
    def condition(self):
        """Return current weather condition."""
        intervals = _forecast_intervals(self._weather_data)

        if not intervals:
            return None

        return _weather_condition(intervals[0].get("wwsymbol_mg2008"))

    @property
    def attribution(self):
        """Return attribution."""
        return "Weather forecast provided by Bosch SmartMowing"

    @property
    def extra_state_attributes(self):
        """Return additional weather attributes."""
        intervals = _forecast_intervals(self._weather_data)

        if not intervals:
            return {}

        current = intervals[0]
        location = (
            self._weather_data
            .get("LocationWeather", {})
            .get("location", {})
        )

        return {
            "location_name": location.get("name"),
            "location_country": location.get("country"),
            "precipitation_probability": current.get("prrr"),
            "precipitation": current.get("rrr"),
            "bosch_weather_symbol": current.get("wwsymbol_mg2008"),
            "interval_length": current.get("intervalLength"),
        }

    async def async_forecast_hourly(self) -> list[Forecast]:
        """Return hourly forecast."""
        forecast = []

        for interval in _forecast_intervals(self._weather_data):
            forecast_time = _parse_datetime(interval.get("dateTime"))

            if forecast_time is None:
                continue

            forecast.append(
                {
                    "datetime": forecast_time.isoformat(),
                    "condition": _weather_condition(
                        interval.get("wwsymbol_mg2008")
                    ),
                    "native_temperature": interval.get("tt"),
                    "precipitation_probability": interval.get("prrr"),
                    "native_precipitation": interval.get("rrr"),
                }
            )

        return forecast

    async def async_forecast_daily(self) -> list[Forecast]:
        """Return daily forecast."""
        intervals = _forecast_intervals(self._weather_data)

        daily = {}

        for interval in intervals:
            dt = _parse_datetime(interval.get("dateTime"))

            if dt is None:
                continue

            day = dt.date().isoformat()

            daily.setdefault(
                day,
                {
                    "temps": [],
                    "rain": [],
                    "prob": [],
                    "condition": interval.get("wwsymbol_mg2008"),
                },
            )

            daily[day]["temps"].append(interval.get("tt"))
            daily[day]["rain"].append(interval.get("rrr"))
            daily[day]["prob"].append(interval.get("prrr"))

        forecast = []

        for day, values in daily.items():
            forecast.append(
                {
                    "datetime": day,
                    "condition": _weather_condition(
                        values["condition"]
                    ),
                    "native_temperature": max(values["temps"]),
                    "templow": min(values["temps"]),
                    "native_precipitation": sum(values["rain"]),
                    "precipitation_probability": max(values["prob"]),
                }
            )

        return forecast
