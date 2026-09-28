from uuid import UUID

from src.application.devices.dto import DeviceDto
from src.application.devices.mappers import device_to_dto
from src.application.locations.dto import (
    LocationConfigRequest,
    LocationConfigResponse,
    LocationSummaryResponse,
    ZoneCreateRequest,
    ZoneResponse,
    ZoneUpdateRequest,
)
from src.application.locations.mappers import (
    domain_to_response,
    request_to_domain,
)
from src.domain.locations.errors import ConfigurationError
from src.infrastructure.persistence.location_repository import (
    LocationRepository,
)


class LocationConfigService:
    def __init__(self, repository: LocationRepository) -> None:
        self.repository = repository

    def create_config(
        self,
        request: LocationConfigRequest,
    ) -> LocationConfigResponse:
        config = request_to_domain(request)

        saved_location = self.repository.save_config(config)

        saved_config = self.repository.get_config(
            saved_location.id
        )

        if saved_config is None:
            raise RuntimeError(
                "Location configuration could not be loaded after saving."
            )

        return domain_to_response(saved_config)

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfigResponse | None:
        config = self.repository.get_config(location_id)

        if config is None:
            return None

        return domain_to_response(config)

    def list_locations(self) -> list[LocationSummaryResponse]:
        locations = self.repository.list_locations()

        return [
            LocationSummaryResponse(
                id=location.id,
                name=location.name,
            )
            for location in locations
        ]

    def delete_location(self, location_id: UUID) -> bool:
        return self.repository.delete_location(location_id)

    def create_zone(
        self,
        location_id: UUID,
        request: ZoneCreateRequest,
    ) -> ZoneResponse | None:
        config = self.repository.get_config(location_id)

        if config is None:
            return None

        self._validate_zone(
            name=request.name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
        )

        zone_name = request.name.strip()

        if any(
            zone.name == zone_name
            for zone in config.location.zones
        ):
            raise ConfigurationError(
                f"Zone name '{zone_name}' must be unique within the location."
            )

        zone_row = self.repository.create_zone(
            location_id=location_id,
            name=zone_name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )

        if zone_row is None:
            return None

        return self._zone_to_response(zone_row)

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        request: ZoneUpdateRequest,
    ) -> ZoneResponse | None:
        config = self.repository.get_config(location_id)

        if config is None:
            return None

        zone_row = self.repository.get_zone(
            location_id,
            zone_id,
        )

        if zone_row is None:
            return None

        self._validate_zone(
            name=request.name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
        )

        zone_name = request.name.strip()

        if any(
            zone.id != zone_id and zone.name == zone_name
            for zone in config.location.zones
        ):
            raise ConfigurationError(
                f"Zone name '{zone_name}' must be unique within the location."
            )

        updated_zone = self.repository.update_zone(
            zone_row=zone_row,
            name=zone_name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )

        return self._zone_to_response(updated_zone)

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> bool:
        config = self.repository.get_config(location_id)

        if config is None:
            return False

        zone_row = self.repository.get_zone(
            location_id,
            zone_id,
        )

        if zone_row is None:
            return False

        if len(config.location.zones) <= 1:
            raise ConfigurationError(
                "A location must have at least one zone."
            )

        self.repository.delete_zone(zone_row)

        return True

    def list_zone_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[DeviceDto] | None:
        config = self.repository.get_config(location_id)

        if config is None:
            return None

        zone = self.repository.get_zone(
            location_id,
            zone_id,
        )

        if zone is None:
            return None

        devices = self.repository.list_devices_for_zone(
            location_id=location_id,
            zone_id=zone_id,
        )

        return [
            device_to_dto(device)
            for device in devices
        ]

    @staticmethod
    def _validate_zone(
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
    ) -> None:
        if not name or not name.strip():
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

    @staticmethod
    def _zone_to_response(zone_row) -> ZoneResponse:
        return ZoneResponse(
            id=zone_row.id,
            location_id=zone_row.location_id,
            name=zone_row.name,
            moisture_threshold_low=float(
                zone_row.moisture_threshold_low
            ),
            moisture_threshold_high=float(
                zone_row.moisture_threshold_high
            ),
            schedule=zone_row.schedule,
        )