from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from src.application.sensors.reading_ingest import (
    ReadingDto,
    ReadingIngest,
)
from src.application.sensors.service import SensorService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.sensor_reading_repository import (
    SensorReadingRepository,
)


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
            raw = (
                values.get("type")
                or values.get("device_type")
                or "moisture"
            )

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


class ReadingResponse(BaseModel):
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime


def get_sensor_service(
    db: Session = Depends(get_db),
) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


def get_reading_ingest(
    db: Session = Depends(get_db),
) -> ReadingIngest:
    device_repository = DeviceRepository(db)
    reading_repository = SensorReadingRepository(db)

    return ReadingIngest(
        device_repository=device_repository,
        reading_repository=reading_repository,
    )


def reading_to_response(
    reading: ReadingDto,
) -> ReadingResponse:
    return ReadingResponse(
        device_id=reading.device_id,
        value=reading.value,
        unit=reading.unit,
        source=reading.source,
        recorded_at=reading.recorded_at,
    )


@router.get(
    "",
    response_model=list[SensorResponse],
)
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


@router.post(
    "/{sensor_id}/read",
    response_model=ReadingResponse,
)
def read_sensor(
    sensor_id: UUID,
    ingest: ReadingIngest = Depends(get_reading_ingest),
):
    try:
        reading = ingest.record(
            device_id=sensor_id,
        )

        return reading_to_response(reading)

    except ValueError as error:
        if str(error).startswith("Device not found:"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{sensor_id}/readings",
    response_model=list[ReadingResponse],
)
def list_sensor_readings(
    sensor_id: UUID,
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    device_repository = DeviceRepository(db)
    device = device_repository.get_device(sensor_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {sensor_id}",
        )

    reading_repository = SensorReadingRepository(db)

    readings = reading_repository.list_for_device(
        device_id=sensor_id,
        limit=limit,
    )

    return [
        ReadingResponse(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )
        for reading in readings
    ]