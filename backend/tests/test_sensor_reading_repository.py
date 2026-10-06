from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.domain.sensors.entity import Reading
from src.infrastructure.persistence.models import Base, DeviceRow
from src.infrastructure.persistence.sensor_reading_repository import (
    SensorReadingRepository,
)


DATABASE_URL = "postgresql+psycopg://greenhouse:greenhouse@localhost:5433/greenhouse"


def test_sensor_reading_repository_saves_reading():
    engine = create_engine(DATABASE_URL)

    device_id = uuid4()

    with Session(engine) as db:
        device = DeviceRow(
            id=device_id,
            device_family="simulation",
            device_type="soil_moisture",
            role="sensor",
            display_name="Test Sensor",
            default_config={"protocol": "simulation"},
            sampling_interval_seconds=10,
            tracking_enabled=True,
        )

        db.add(device)
        db.commit()

        reading = Reading(
            device_id=device_id,
            value=0.42,
            unit="vwc",
            source="simulation",
            recorded_at=datetime.now(timezone.utc),
        )

        repository = SensorReadingRepository(db)
        saved = repository.save(reading)

        assert saved.device_id == device_id
        assert saved.value == 0.42
        assert saved.unit == "vwc"
        assert saved.source == "simulation"
        assert saved.recorded_at.tzinfo is not None

        db.delete(device)
        db.commit()

    engine.dispose()