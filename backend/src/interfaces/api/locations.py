from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.locations.config_service import LocationConfigService
from src.application.locations.dto import (
    LocationConfigRequest,
    LocationConfigResponse,
    LocationSummaryResponse,
    ZoneCreateRequest,
    ZoneResponse,
    ZoneUpdateRequest,
)
from src.application.devices.dto import DeviceDto
from src.domain.locations.errors import ConfigurationError
from src.infrastructure.db import get_db
from src.infrastructure.persistence.location_repository import (
    LocationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_location_config_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    repository = LocationRepository(db)
    return LocationConfigService(repository)


@router.post(
    "/config",
    response_model=LocationConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: LocationConfigRequest,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> LocationConfigResponse:
    try:
        return service.create_config(request)
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigResponse,
)
def get_location_config(
    location_id: UUID,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> LocationConfigResponse:
    config = service.get_config(location_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    return config


@router.get(
    "",
    response_model=list[LocationSummaryResponse],
)
def list_locations(
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> list[LocationSummaryResponse]:
    return service.list_locations()


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> None:
    deleted = service.delete_location(location_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )


@router.post(
    "/{location_id}/zones",
    response_model=ZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_zone(
    location_id: UUID,
    request: ZoneCreateRequest,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> ZoneResponse:
    try:
        zone = service.create_zone(
            location_id=location_id,
            request=request,
        )
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    return zone


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneResponse,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneUpdateRequest,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> ZoneResponse:
    try:
        zone = service.update_zone(
            location_id=location_id,
            zone_id=zone_id,
            request=request,
        )
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location or zone not found.",
        )

    return zone


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> None:
    try:
        deleted = service.delete_zone(
            location_id=location_id,
            zone_id=zone_id,
        )
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location or zone not found.",
        )


@router.get(
    "/{location_id}/zones/{zone_id}/devices",
    response_model=list[DeviceDto],
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(
        get_location_config_service
    ),
) -> list[DeviceDto]:
    devices = service.list_zone_devices(
        location_id=location_id,
        zone_id=zone_id,
    )

    if devices is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location or zone not found.",
        )

    return devices