from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from src.application.sensors.service import SensorService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class SensorCreateRequest(BaseModel):
    type: str | None = None
    device_type: str | None = None
    display_name: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            raw = values.get("type") or values.get("device_type") or "moisture"
            # Normalize to the exact keys creators.py uses ("moisture" / "light")
            if "light" in raw.lower():
                normalized = "light"
            else:
                normalized = "moisture"
            values["type"] = normalized
            values["device_type"] = normalized
        return values


class SensorResponse(BaseModel):
    id: UUID | str
    device_type: str
    display_name: str | None
    default_config: dict


def get_sensor_service(db: Session = Depends(get_db)) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    service: SensorService = Depends(get_sensor_service),
):
    return service.list_sensors()


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    service: SensorService = Depends(get_sensor_service),
):
    try:
        chosen_type = request.type or "moisture"
        return service.create_sensor(
            sensor_type=chosen_type,
            display_name=request.display_name,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
