from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import devices_to_dtos
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


def get_device_family_service(db: Session = Depends(get_db)) -> DeviceFamilyService:
    repository = DeviceRepository(db)
    return DeviceFamilyService(repository)


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(default=None, description="Filter by device family (e.g. 'simulation', 'edge')"),
    role: str | None = Query(default=None, description="Filter by device role ('sensor' or 'actuator')"),
    service: DeviceFamilyService = Depends(get_device_family_service),
) -> list[DeviceDto]:
    domain_devices = service.list_devices(device_family=family, role=role)
    return devices_to_dtos(domain_devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_device_family(
    family: str = Query(..., description="Device family key to provision (e.g. 'simulation', 'edge')"),
    service: DeviceFamilyService = Depends(get_device_family_service),
) -> list[DeviceDto]:
    try:
        created_devices = service.provision_family(family)
        return devices_to_dtos(created_devices)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
