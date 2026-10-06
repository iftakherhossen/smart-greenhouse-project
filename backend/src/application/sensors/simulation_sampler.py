from datetime import datetime, timezone
from uuid import UUID

from src.application.sensors.reading_ingest import ReadingDto, ReadingIngest
from src.infrastructure.persistence.device_repository import DeviceRepository


class SimulationSampler:
    """
    Periodically samples enabled simulation sensors.

    The sampler keeps the last successful sample time in memory.
    The `now` argument makes the timing logic deterministic and easy to test.
    """

    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_ingest: ReadingIngest,
    ):
        self._device_repository = device_repository
        self._reading_ingest = reading_ingest
        self._last_sampled_at: dict[UUID, datetime] = {}

    def run_once(
        self,
        now: datetime | None = None,
    ) -> list[ReadingDto]:
        if now is None:
            now = datetime.now(timezone.utc)

        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware.")

        devices = self._device_repository.list_devices(
            device_family="simulation",
            role="sensor",
        )

        readings: list[ReadingDto] = []

        for device in devices:
            if device.id is None:
                continue

            if not device.tracking_enabled:
                continue

            last_sampled = self._last_sampled_at.get(device.id)

            if last_sampled is not None:
                elapsed_seconds = (
                    now - last_sampled
                ).total_seconds()

                if elapsed_seconds < device.sampling_interval_seconds:
                    continue

            reading = self._reading_ingest.record(
                device_id=device.id,
                now=now,
            )

            self._last_sampled_at[device.id] = now
            readings.append(reading)

        return readings