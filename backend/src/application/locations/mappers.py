from src.application.locations.dto import (
    LocationConfigRequest,
    LocationConfigResponse,
    LocationSummaryResponse,
    ZoneResponse,
)
from src.domain.locations.config_builder import LocationConfigBuilder
from src.domain.locations.entity import Location, LocationConfig


def request_to_domain(request: LocationConfigRequest) -> LocationConfig:
    builder = LocationConfigBuilder()

    builder.with_location_name(request.location_name)

    for zone in request.zones:
        builder.add_zone(
            name=zone.name,
            moisture_threshold_low=zone.moisture_threshold_low,
            moisture_threshold_high=zone.moisture_threshold_high,
            schedule=zone.schedule,
        )

    return builder.build()


def domain_to_response(config: LocationConfig) -> LocationConfigResponse:
    location = config.location

    if location.id is None:
        raise ValueError("Location ID is required for a response.")

    zones = []

    for zone in location.zones:
        if zone.id is None:
            raise ValueError("Zone ID is required for a response.")

        zones.append(
            ZoneResponse(
                id=zone.id,
                location_id=location.id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )
        )

    return LocationConfigResponse(
        location=LocationSummaryResponse(
            id=location.id,
            name=location.name,
        ),
        zones=zones,
    )