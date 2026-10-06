from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.sensors.entity import Reading
from src.infrastructure.persistence.models import SensorReadingRow


class SensorReadingRepository:
    def __init__(self, db: Session):
        self._db = db

    def save(self, reading: Reading) -> Reading:
        row = SensorReadingRow(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )

    def list_for_device(
        self,
        device_id: UUID,
        *,
        limit: int = 50,
    ) -> list[Reading]:
        statement = (
            select(SensorReadingRow)
            .where(SensorReadingRow.device_id == device_id)
            .order_by(SensorReadingRow.recorded_at.desc())
            .limit(limit)
        )

        rows = self._db.scalars(statement).all()

        return [
            Reading(
                device_id=row.device_id,
                value=float(row.value),
                unit=row.unit,
                source=row.source,
                recorded_at=row.recorded_at,
            )
            for row in rows
        ]

    def latest_for_device(
        self,
        device_id: UUID,
    ) -> Reading | None:
        statement = (
            select(SensorReadingRow)
            .where(SensorReadingRow.device_id == device_id)
            .order_by(SensorReadingRow.recorded_at.desc())
            .limit(1)
        )

        row = self._db.scalars(statement).first()

        if row is None:
            return None

        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )