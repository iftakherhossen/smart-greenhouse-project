from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import devices_to_dtos
from src.application.locations.dto import DeviceZoneAssignmentRequest
from src.application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from src.application.sensors.sampling_service import SamplingDto, SamplingService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


class SamplingUpdateRequest(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool


class SamplingResponse(BaseModel):
    device_id: UUID
    sampling_interval_seconds: int
    tracking_enabled: bool


def get_device_family_service(
    db: Session = Depends(get_db),
) -> DeviceFamilyService:
    repository = DeviceRepository(db)
    return DeviceFamilyService(repository)


def get_zone_assignment_service(
    db: Session = Depends(get_db),
) -> ZoneAssignmentService:
    repository = DeviceRepository(db)
    return ZoneAssignmentService(repository)


def get_sampling_service(
    db: Session = Depends(get_db),
) -> SamplingService:
    repository = DeviceRepository(db)
    return SamplingService(repository)


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(
        default=None,
        description="Filter by device family (e.g. 'simulation', 'edge')",
    ),
    role: str | None = Query(
        default=None,
        description="Filter by device role ('sensor' or 'actuator')",
    ),
    service: DeviceFamilyService = Depends(
        get_device_family_service
    ),
) -> list[DeviceDto]:
    domain_devices = service.list_devices(
        device_family=family,
        role=role,
    )

    return devices_to_dtos(domain_devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_device_family(
    family: str = Query(
        ...,
        description="Device family key to provision (e.g. 'simulation', 'edge')",
    ),
    service: DeviceFamilyService = Depends(
        get_device_family_service
    ),
) -> list[DeviceDto]:
    try:
        created_devices = service.provision_family(family)
        return devices_to_dtos(created_devices)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.patch(
    "/{device_id}/sampling",
    response_model=SamplingResponse,
)
def update_sampling(
    device_id: UUID,
    request: SamplingUpdateRequest,
    service: SamplingService = Depends(
        get_sampling_service
    ),
) -> SamplingResponse:
    try:
        result: SamplingDto = service.update(
            device_id=device_id,
            sampling_interval_seconds=request.sampling_interval_seconds,
            tracking_enabled=request.tracking_enabled,
        )

        return SamplingResponse(
            device_id=result.device_id,
            sampling_interval_seconds=result.sampling_interval_seconds,
            tracking_enabled=result.tracking_enabled,
        )

    except ValueError as error:
        message = str(error)

        if message.startswith("Device not found"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.put(
    "/{device_id}/zone",
)
def assign_device_zone(
    device_id: UUID,
    request: DeviceZoneAssignmentRequest,
    service: ZoneAssignmentService = Depends(
        get_zone_assignment_service
    ),
):
    try:
        if request.zone_id is None:
            device = service.unassign_device(device_id)
        else:
            device = service.assign_device(
                device_id=device_id,
                zone_id=request.zone_id,
            )

        return {
            "device_id": device.id,
            "zone_id": device.zone_id,
            "location_id": device.location_id,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )