from src.infrastructure.sensors.adapter_selector import select_sensor_adapter
from src.infrastructure.sensors.mqtt_adapter import MqttSensorAdapter
from src.infrastructure.sensors.simulation_adapter import SimulationSensorAdapter
from src.infrastructure.sensors.vendor_stub_adapter import VendorStubAdapter


def test_selects_simulation_adapter():
    adapter = select_sensor_adapter(
        device_type="moisture_sensor",
        default_config={"protocol": "simulation"},
    )

    assert isinstance(adapter, SimulationSensorAdapter)


def test_selects_mqtt_adapter():
    adapter = select_sensor_adapter(
        device_type="moisture_sensor",
        default_config={"protocol": "mqtt"},
    )

    assert isinstance(adapter, MqttSensorAdapter)


def test_selects_vendor_stub_when_driver_is_set():
    adapter = select_sensor_adapter(
        device_type="moisture_sensor",
        default_config={
            "protocol": "simulation",
            "driver": "vendor_stub",
        },
    )

    assert isinstance(adapter, VendorStubAdapter)


def test_rejects_unsupported_configuration():
    import pytest

    with pytest.raises(ValueError, match="Unsupported sensor configuration"):
        select_sensor_adapter(
            device_type="moisture_sensor",
            default_config={"protocol": "unknown"},
        )