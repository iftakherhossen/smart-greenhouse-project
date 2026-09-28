from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.devices.entity import Device
from src.domain.locations.entity import Location, LocationConfig, Zone
from src.infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ZoneRow,
)


class LocationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_config(self, config: LocationConfig) -> LocationRow:
        location = config.location

        location_row = LocationRow(
            name=location.name,
        )

        self.db.add(location_row)
        self.db.flush()

        for zone in location.zones:
            zone_row = ZoneRow(
                location_id=location_row.id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

            self.db.add(zone_row)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(location_row)

        return location_row

    def get_config(self, location_id: UUID) -> LocationConfig | None:
        location_row = self.db.get(LocationRow, location_id)

        if location_row is None:
            return None

        zone_rows = (
            self.db.query(ZoneRow)
            .filter(ZoneRow.location_id == location_id)
            .order_by(ZoneRow.name)
            .all()
        )

        zones = tuple(
            Zone(
                id=zone_row.id,
                name=zone_row.name,
                moisture_threshold_low=float(
                    zone_row.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    zone_row.moisture_threshold_high
                ),
                schedule=zone_row.schedule,
            )
            for zone_row in zone_rows
        )

        location = Location(
            id=location_row.id,
            name=location_row.name,
            zones=zones,
        )

        return LocationConfig(location=location)

    def list_locations(self) -> list[LocationRow]:
        return (
            self.db.query(LocationRow)
            .order_by(LocationRow.name)
            .all()
        )

    def delete_location(self, location_id: UUID) -> bool:
        location_row = self.db.get(LocationRow, location_id)

        if location_row is None:
            return False

        try:
            self.db.delete(location_row)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return True

    def create_zone(
        self,
        location_id: UUID,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow | None:
        location_row = self.db.get(LocationRow, location_id)

        if location_row is None:
            return None

        zone_row = ZoneRow(
            location_id=location_id,
            name=name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule,
        )

        try:
            self.db.add(zone_row)
            self.db.commit()
            self.db.refresh(zone_row)
        except Exception:
            self.db.rollback()
            raise

        return zone_row

    def get_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        return (
            self.db.query(ZoneRow)
            .filter(
                ZoneRow.id == zone_id,
                ZoneRow.location_id == location_id,
            )
            .first()
        )

    def count_zones(self, location_id: UUID) -> int:
        return (
            self.db.query(ZoneRow)
            .filter(ZoneRow.location_id == location_id)
            .count()
        )

    def update_zone(
        self,
        zone_row: ZoneRow,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow:
        zone_row.name = name
        zone_row.moisture_threshold_low = moisture_threshold_low
        zone_row.moisture_threshold_high = moisture_threshold_high
        zone_row.schedule = schedule

        try:
            self.db.commit()
            self.db.refresh(zone_row)
        except Exception:
            self.db.rollback()
            raise

        return zone_row

    def clear_device_zone_assignment(
        self,
        zone_id: UUID,
    ) -> None:
        devices = (
            self.db.query(DeviceRow)
            .filter(DeviceRow.zone_id == zone_id)
            .all()
        )

        for device in devices:
            device.zone_id = None
            device.location_id = None

    def delete_zone(
        self,
        zone_row: ZoneRow,
    ) -> None:
        try:
            self.clear_device_zone_assignment(zone_row.id)
            self.db.delete(zone_row)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def list_devices_for_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[Device]:
        rows = (
            self.db.query(DeviceRow)
            .filter(
                DeviceRow.zone_id == zone_id,
                DeviceRow.location_id == location_id,
            )
            .order_by(DeviceRow.created_at)
            .all()
        )

        return [
            Device(
                id=row.id,
                device_type=row.device_type,
                role=row.role,
                device_family=row.device_family,
                display_name=row.display_name or row.device_type,
                default_config=row.default_config,
                zone_id=row.zone_id,
                location_id=row.location_id,
            )
            for row in rows
        ]