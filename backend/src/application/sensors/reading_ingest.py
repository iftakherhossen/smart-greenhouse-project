from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.entity import Reading
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.sensor_reading_repository import (
    SensorReadingRepository,
)
from src.infrastructure.sensors.adapter_selector import select_sensor_adapter


@dataclass(frozen=True)
class ReadingDto:
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime


class ReadingIngest:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: SensorReadingRepository,
    ):
        self._device_repository = device_repository
        self._reading_repository = reading_repository

    def record(
        self,
        device_id: UUID,
        *,
        now: datetime | None = None,
        reading: Reading | None = None,
    ) -> ReadingDto:
        device = self._device_repository.get_device(device_id)

        if device is None:
            raise ValueError(f"Device not found: {device_id}")

        if device.role != "sensor":
            raise ValueError(
                f"Device '{device_id}' is not a sensor."
            )

        if reading is None:
            recorded_at = now or datetime.now(timezone.utc)

            adapter = select_sensor_adapter(
                device_type=device.device_type,
                default_config=device.default_config,
            )

            if not hasattr(adapter, "read"):
                raise ValueError(
                    "Selected adapter does not support direct reads."
                )

            reading = adapter.read(
                device_id=device_id,
                now=recorded_at,
            )

        if reading.device_id != device_id:
            raise ValueError(
                "Reading device_id does not match the requested device."
            )

        saved_reading = self._reading_repository.save(reading)

        return ReadingDto(
            device_id=saved_reading.device_id,
            value=saved_reading.value,
            unit=saved_reading.unit,
            source=saved_reading.source,
            recorded_at=saved_reading.recorded_at,
        )