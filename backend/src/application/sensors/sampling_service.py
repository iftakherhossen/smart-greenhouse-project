from dataclasses import dataclass
from uuid import UUID

from src.infrastructure.persistence.device_repository import DeviceRepository


@dataclass(frozen=True)
class SamplingDto:
    device_id: UUID
    sampling_interval_seconds: int
    tracking_enabled: bool


class SamplingService:
    def __init__(self, device_repository: DeviceRepository):
        self._device_repository = device_repository

    def update(
        self,
        device_id: UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> SamplingDto:
        if sampling_interval_seconds < 5:
            raise ValueError(
                "Sampling interval must be at least 5 seconds."
            )

        device = self._device_repository.update_sampling(
            device_id=device_id,
            sampling_interval_seconds=sampling_interval_seconds,
            tracking_enabled=tracking_enabled,
        )

        if device is None:
            raise ValueError(f"Device not found: {device_id}")

        return SamplingDto(
            device_id=device.id,
            sampling_interval_seconds=device.sampling_interval_seconds,
            tracking_enabled=device.tracking_enabled,
        )
        