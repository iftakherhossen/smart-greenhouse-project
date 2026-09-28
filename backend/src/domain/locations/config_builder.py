from typing import Any

from src.domain.locations.entity import Location, LocationConfig, Zone
from src.domain.locations.errors import ConfigurationError


class LocationConfigBuilder:
    def __init__(self) -> None:
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def with_location_name(self, name: str) -> "LocationConfigBuilder":
        if not name or not name.strip():
            raise ConfigurationError("Location name is required.")

        self._location_name = name.strip()
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict[str, Any] | None = None,
    ) -> "LocationConfigBuilder":
        zone_name = name.strip()

        if not zone_name:
            raise ConfigurationError("Zone name is required.")

        if not 0.0 <= moisture_threshold_low <= 1.0:
            raise ConfigurationError(
                "Low moisture threshold must be between 0.0 and 1.0."
            )

        if not 0.0 <= moisture_threshold_high <= 1.0:
            raise ConfigurationError(
                "High moisture threshold must be between 0.0 and 1.0."
            )

        if moisture_threshold_low >= moisture_threshold_high:
            raise ConfigurationError(
                "Low moisture threshold must be lower than high threshold."
            )

        if any(zone.name == zone_name for zone in self._zones):
            raise ConfigurationError(
                f"Zone name '{zone_name}' must be unique within the location."
            )

        self._zones.append(
            Zone(
                name=zone_name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=schedule or {},
            )
        )

        return self

    def build(self) -> LocationConfig:
        if not self._location_name:
            raise ConfigurationError("Location name is required.")

        if not self._zones:
            raise ConfigurationError(
                "At least one zone is required."
            )

        location = Location(
            name=self._location_name,
            zones=tuple(self._zones),
        )

        return LocationConfig(location=location)