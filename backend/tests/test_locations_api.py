import pytest

from src.application.locations.config_service import LocationConfigService
from src.application.locations.dto import (
    LocationConfigRequest,
    ZoneCreateRequest,
    ZoneUpdateRequest,
    ZoneConfigRequest,
)
from src.application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from src.domain.locations.errors import ConfigurationError
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.location_repository import (
    LocationRepository,
)
from src.infrastructure.persistence.models import DeviceRow


def create_location_config():
    return LocationConfigRequest(
        location_name="API Test Greenhouse",
        zones=[
            ZoneConfigRequest(
                name="Zone A",
                moisture_threshold_low=0.3,
                moisture_threshold_high=0.7,
                schedule={},
            ),
            ZoneConfigRequest(
                name="Zone B",
                moisture_threshold_low=0.2,
                moisture_threshold_high=0.8,
                schedule={},
            ),
        ],
    )


def create_device(db, name: str) -> DeviceRow:
    device = DeviceRow(
        device_family="simulation",
        device_type="soil_moisture",
        role="sensor",
        display_name=name,
        default_config={},
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def test_create_and_get_location_config():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        request = create_location_config()

        created = service.create_config(request)

        assert created.location.name == "API Test Greenhouse"
        assert len(created.zones) == 2

        location_id = created.location.id

        loaded = service.get_config(location_id)

        assert loaded is not None
        assert loaded.location.id == location_id
        assert loaded.location.name == "API Test Greenhouse"
        assert len(loaded.zones) == 2


def test_create_location_rejects_invalid_thresholds():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        request = LocationConfigRequest(
            location_name="Invalid Greenhouse",
            zones=[
                ZoneConfigRequest(
                    name="Zone A",
                    moisture_threshold_low=0.8,
                    moisture_threshold_high=0.4,
                    schedule={},
                )
            ],
        )

        with pytest.raises(
            ConfigurationError,
            match="Low moisture threshold must be lower than high threshold",
        ):
            service.create_config(request)


def test_create_location_rejects_duplicate_zones():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        request = LocationConfigRequest(
            location_name="Duplicate Greenhouse",
            zones=[
                ZoneConfigRequest(
                    name="Zone A",
                    moisture_threshold_low=0.3,
                    moisture_threshold_high=0.7,
                    schedule={},
                ),
                ZoneConfigRequest(
                    name="Zone A",
                    moisture_threshold_low=0.2,
                    moisture_threshold_high=0.8,
                    schedule={},
                ),
            ],
        )

        with pytest.raises(
            ConfigurationError,
            match="must be unique within the location",
        ):
            service.create_config(request)


def test_assign_two_devices_to_same_zone():
    with SessionLocal() as db:
        location_repository = LocationRepository(db)
        location_service = LocationConfigService(
            location_repository
        )

        created = location_service.create_config(
            create_location_config()
        )

        location_id = created.location.id
        zone_id = created.zones[0].id

        device_one = create_device(
            db,
            "Zone Test Device 1",
        )

        device_two = create_device(
            db,
            "Zone Test Device 2",
        )

        device_repository = DeviceRepository(db)
        assignment_service = ZoneAssignmentService(
            device_repository
        )

        assigned_one = assignment_service.assign_device(
            device_id=device_one.id,
            zone_id=zone_id,
        )

        assigned_two = assignment_service.assign_device(
            device_id=device_two.id,
            zone_id=zone_id,
        )

        assert assigned_one.zone_id == zone_id
        assert assigned_two.zone_id == zone_id

        assert assigned_one.location_id == location_id
        assert assigned_two.location_id == location_id


def test_list_devices_for_zone_only_returns_devices_in_that_zone():
    with SessionLocal() as db:
        location_repository = LocationRepository(db)
        location_service = LocationConfigService(
            location_repository
        )

        created = location_service.create_config(
            create_location_config()
        )

        location_id = created.location.id
        zone_a_id = created.zones[0].id
        zone_b_id = created.zones[1].id

        device_one = create_device(
            db,
            "Zone A Device",
        )

        device_two = create_device(
            db,
            "Zone B Device",
        )

        device_repository = DeviceRepository(db)
        assignment_service = ZoneAssignmentService(
            device_repository
        )

        assignment_service.assign_device(
            device_id=device_one.id,
            zone_id=zone_a_id,
        )

        assignment_service.assign_device(
            device_id=device_two.id,
            zone_id=zone_b_id,
        )

        devices = location_service.list_zone_devices(
            location_id=location_id,
            zone_id=zone_a_id,
        )

        assert devices is not None

        device_ids = {
            device.id
            for device in devices
        }

        assert device_one.id in device_ids
        assert device_two.id not in device_ids


def test_unassign_device_clears_zone_and_location():
    with SessionLocal() as db:
        location_repository = LocationRepository(db)
        location_service = LocationConfigService(
            location_repository
        )

        created = location_service.create_config(
            create_location_config()
        )

        zone_id = created.zones[0].id

        device = create_device(
            db,
            "Unassign Test Device",
        )

        device_repository = DeviceRepository(db)
        assignment_service = ZoneAssignmentService(
            device_repository
        )

        assigned = assignment_service.assign_device(
            device_id=device.id,
            zone_id=zone_id,
        )

        assert assigned.zone_id == zone_id
        assert assigned.location_id == created.location.id

        unassigned = assignment_service.unassign_device(
            device_id=device.id,
        )

        assert unassigned.zone_id is None
        assert unassigned.location_id is None


def test_create_update_and_delete_zone():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        created = service.create_config(
            create_location_config()
        )

        location_id = created.location.id

        new_zone = service.create_zone(
            location_id=location_id,
            request=ZoneCreateRequest(
                name="Zone C",
                moisture_threshold_low=0.25,
                moisture_threshold_high=0.75,
                schedule={"watering": "09:00"},
            ),
        )

        assert new_zone is not None
        assert new_zone.name == "Zone C"

        updated_zone = service.update_zone(
            location_id=location_id,
            zone_id=new_zone.id,
            request=ZoneUpdateRequest(
                name="Updated Zone C",
                moisture_threshold_low=0.35,
                moisture_threshold_high=0.65,
                schedule={"watering": "10:00"},
            ),
        )

        assert updated_zone is not None
        assert updated_zone.name == "Updated Zone C"
        assert updated_zone.moisture_threshold_low == 0.35
        assert updated_zone.moisture_threshold_high == 0.65

        deleted = service.delete_zone(
            location_id=location_id,
            zone_id=new_zone.id,
        )

        assert deleted is True


def test_zone_update_rejects_invalid_thresholds():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        created = service.create_config(
            create_location_config()
        )

        with pytest.raises(
            ConfigurationError,
            match="Low moisture threshold must be lower than high threshold",
        ):
            service.update_zone(
                location_id=created.location.id,
                zone_id=created.zones[0].id,
                request=ZoneUpdateRequest(
                    name="Invalid Zone",
                    moisture_threshold_low=0.9,
                    moisture_threshold_high=0.4,
                    schedule={},
                ),
            )


def test_last_zone_cannot_be_deleted():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        request = LocationConfigRequest(
            location_name="Single Zone Greenhouse",
            zones=[
                ZoneConfigRequest(
                    name="Only Zone",
                    moisture_threshold_low=0.3,
                    moisture_threshold_high=0.7,
                    schedule={},
                )
            ],
        )

        created = service.create_config(request)

        with pytest.raises(
            ConfigurationError,
            match="at least one zone",
        ):
            service.delete_zone(
                location_id=created.location.id,
                zone_id=created.zones[0].id,
            )


def test_delete_location():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        created = service.create_config(
            create_location_config()
        )

        location_id = created.location.id

        deleted = service.delete_location(location_id)

        assert deleted is True
        assert service.get_config(location_id) is None


def test_missing_location_returns_none():
    with SessionLocal() as db:
        repository = LocationRepository(db)
        service = LocationConfigService(repository)

        result = service.get_config(
            __import__("uuid").uuid4()
        )

        assert result is None