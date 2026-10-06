from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import Mock

from src.application.sensors.simulation_sampler import SimulationSampler
from src.application.sensors.reading_ingest import ReadingDto
from src.domain.devices.entity import Device


def test_sampler_respects_sampling_interval():
    device_id = uuid4()

    device = Device(
        id=device_id,
        device_type="soil_moisture",
        role="sensor",
        device_family="simulation",
        display_name="Test Soil Moisture Sensor",
        default_config={"protocol": "simulation"},
        sampling_interval_seconds=10,
        tracking_enabled=True,
    )

    device_repository = Mock()
    device_repository.list_devices.return_value = [device]

    reading_ingest = Mock()

    now = datetime.now(timezone.utc)

    reading_ingest.record.return_value = ReadingDto(
        device_id=device_id,
        value=0.4,
        unit="vwc",
        source="simulation",
        recorded_at=now,
    )

    sampler = SimulationSampler(
        device_repository=device_repository,
        reading_ingest=reading_ingest,
    )

    # First run should create a reading.
    first = sampler.run_once(now)

    assert len(first) == 1
    assert reading_ingest.record.call_count == 1

    # Five seconds later is too early.
    second = sampler.run_once(
        now + timedelta(seconds=5)
    )

    assert len(second) == 0
    assert reading_ingest.record.call_count == 1

    # Ten seconds after the first reading should trigger another reading.
    third = sampler.run_once(
        now + timedelta(seconds=10)
    )

    assert len(third) == 1
    assert reading_ingest.record.call_count == 2


def test_sampler_skips_disabled_tracking():
    device_id = uuid4()

    device = Device(
        id=device_id,
        device_type="soil_moisture",
        role="sensor",
        device_family="simulation",
        display_name="Disabled Test Sensor",
        default_config={"protocol": "simulation"},
        sampling_interval_seconds=10,
        tracking_enabled=False,
    )

    device_repository = Mock()
    device_repository.list_devices.return_value = [device]

    reading_ingest = Mock()

    sampler = SimulationSampler(
        device_repository=device_repository,
        reading_ingest=reading_ingest,
    )

    now = datetime.now(timezone.utc)

    result = sampler.run_once(now)

    assert result == []
    reading_ingest.record.assert_not_called()