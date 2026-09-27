import pytest
from src.domain.devices.entity import Device
from src.domain.devices.family_factory import (
    EdgeHardwareFactory,
    SimulationDeviceFactory,
    get_family_factory,
)


def test_device_entity_validation():
    dev = Device(
        device_type="test_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test Sensor",
    )
    assert dev.role == "sensor"
    assert dev.device_family == "simulation"

    with pytest.raises(ValueError, match="Invalid device role"):
        Device(
            device_type="test_bad",
            role="invalid_role",
            device_family="simulation",
            display_name="Bad Role",
        )


def test_simulation_device_factory():
    factory = SimulationDeviceFactory()
    assert factory.family_key == "simulation"

    devices = factory.create_device_set()
    assert len(devices) == 4

    sensors = [d for d in devices if d.role == "sensor"]
    actuators = [d for d in devices if d.role == "actuator"]
    assert len(sensors) == 2
    assert len(actuators) == 2

    assert all(d.device_family == "simulation" for d in devices)
    assert any(d.device_type == "moisture_sensor" for d in sensors)
    assert any(d.device_type == "light_sensor" for d in sensors)
    assert any(d.device_type == "water_pump" for d in actuators)
    assert any(d.device_type == "grow_light" for d in actuators)

    for s in sensors:
        assert s.default_config.get("protocol") == "sim_virtual_bus"


def test_edge_hardware_factory():
    factory = EdgeHardwareFactory()
    assert factory.family_key == "edge"

    devices = factory.create_device_set()
    assert len(devices) == 4

    sensors = [d for d in devices if d.role == "sensor"]
    actuators = [d for d in devices if d.role == "actuator"]
    assert len(sensors) == 2
    assert len(actuators) == 2

    assert all(d.device_family == "edge" for d in devices)

    moisture = next(d for d in sensors if d.device_type == "moisture_sensor")
    light = next(d for d in sensors if d.device_type == "light_sensor")
    pump = next(d for d in actuators if d.device_type == "water_pump")
    grow_light = next(d for d in actuators if d.device_type == "grow_light")

    assert moisture.default_config["protocol"] == "i2c"
    assert light.default_config["protocol"] == "spi"
    assert pump.default_config["protocol"] == "gpio-relay"
    assert grow_light.default_config["protocol"] == "pwm"


def test_get_family_factory():
    sim = get_family_factory("simulation")
    assert isinstance(sim, SimulationDeviceFactory)

    edge = get_family_factory("edge")
    assert isinstance(edge, EdgeHardwareFactory)

    with pytest.raises(ValueError, match="Unknown device family"):
        get_family_factory("cloud")