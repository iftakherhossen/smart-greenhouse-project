import pytest
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import devices_to_dtos


def test_provision_simulation_kit_service():
    with SessionLocal() as db:
        repo = DeviceRepository(db)
        service = DeviceFamilyService(repo)

        devices = service.provision_family("simulation")
        assert len(devices) == 4
        assert all(d.device_family == "simulation" for d in devices)

        roles = {d.role for d in devices}
        assert roles == {"sensor", "actuator"}

        dtos = devices_to_dtos(devices)
        assert len(dtos) == 4
        assert all(d.id is not None for d in dtos)


def test_provision_edge_kit_service():
    with SessionLocal() as db:
        repo = DeviceRepository(db)
        service = DeviceFamilyService(repo)

        devices = service.provision_family("edge")
        assert len(devices) == 4
        assert all(d.device_family == "edge" for d in devices)

        protocols = {d.default_config.get("protocol") for d in devices}
        assert "i2c" in protocols or "spi" in protocols or "gpio-relay" in protocols


def test_provision_unknown_family_raises_value_error():
    with SessionLocal() as db:
        repo = DeviceRepository(db)
        service = DeviceFamilyService(repo)

        with pytest.raises(ValueError, match="Unknown device family"):
            service.provision_family("invalid_family")


def test_list_devices_filtering_service():
    with SessionLocal() as db:
        repo = DeviceRepository(db)
        service = DeviceFamilyService(repo)

        # Provision kits to ensure data presence
        service.provision_family("simulation")
        service.provision_family("edge")

        edge_devices = service.list_devices(device_family="edge")
        assert len(edge_devices) >= 4
        assert all(d.device_family == "edge" for d in edge_devices)

        actuator_devices = service.list_devices(role="actuator")
        assert len(actuator_devices) >= 4
        assert all(d.role == "actuator" for d in actuator_devices)
