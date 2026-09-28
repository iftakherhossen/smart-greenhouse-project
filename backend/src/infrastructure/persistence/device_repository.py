from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.devices.entity import Device
from src.domain.sensors.entity import Sensor
from src.infrastructure.persistence.models import (
    DeviceRow,
    ZoneRow,
)


class DeviceRepository:
    def __init__(self, db: Session):
        self._db = db

    # --- Phase 2 Compatibility Methods ---
    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_family="simulation",
            device_type=sensor.device_type,
            role="sensor",
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        sensor.id = row.id
        return sensor

    def list_sensors(self) -> list[Sensor]:
        statement = (
            select(DeviceRow)
            .where(DeviceRow.role == "sensor")
            .order_by(DeviceRow.created_at)
        )

        rows = self._db.scalars(statement).all()

        return [
            Sensor(
                id=row.id,
                device_type=row.device_type,
                display_name=row.display_name,
                default_config=row.default_config,
            )
            for row in rows
        ]

    # --- Phase 3 Device Methods ---
    def save_device(self, device: Device) -> Device:
        row = DeviceRow(
            device_family=device.device_family,
            device_type=device.device_type,
            role=device.role,
            display_name=device.display_name,
            default_config=device.default_config,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return self._row_to_device(row)

    def save_devices(self, devices: list[Device]) -> list[Device]:
        rows = [
            DeviceRow(
                device_family=d.device_family,
                device_type=d.device_type,
                role=d.role,
                display_name=d.display_name,
                default_config=d.default_config,
            )
            for d in devices
        ]

        self._db.add_all(rows)
        self._db.commit()

        for row in rows:
            self._db.refresh(row)

        return [self._row_to_device(r) for r in rows]

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow).order_by(DeviceRow.created_at)

        if device_family:
            statement = statement.where(
                DeviceRow.device_family == device_family
            )

        if role:
            statement = statement.where(
                DeviceRow.role == role
            )

        rows = self._db.scalars(statement).all()

        return [self._row_to_device(r) for r in rows]

    # --- Phase 4 Zone Assignment Methods ---
    def get_device_row(
        self,
        device_id: UUID,
    ) -> DeviceRow | None:
        return self._db.get(DeviceRow, device_id)

    def get_zone_row(
        self,
        zone_id: UUID,
    ) -> ZoneRow | None:
        return self._db.get(ZoneRow, zone_id)

    def assign_device_to_zone(
        self,
        device_row: DeviceRow,
        zone_row: ZoneRow,
    ) -> DeviceRow:
        device_row.zone_id = zone_row.id
        device_row.location_id = zone_row.location_id

        try:
            self._db.commit()
            self._db.refresh(device_row)
        except Exception:
            self._db.rollback()
            raise

        return device_row

    def unassign_device_from_zone(
        self,
        device_row: DeviceRow,
    ) -> DeviceRow:
        device_row.zone_id = None
        device_row.location_id = None

        try:
            self._db.commit()
            self._db.refresh(device_row)
        except Exception:
            self._db.rollback()
            raise

        return device_row

    @staticmethod
    def _row_to_device(row: DeviceRow) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or row.device_type,
            default_config=row.default_config,
            zone_id=row.zone_id,
            location_id=row.location_id,
        )