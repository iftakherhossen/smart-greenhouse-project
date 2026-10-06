from datetime import datetime, timezone
from uuid import uuid4

from src.infrastructure.sensors.simulation_adapter import SimulationSensorAdapter


def test_soil_moisture_value_is_in_range():
    adapter = SimulationSensorAdapter("soil_moisture")

    reading = adapter.read(
        device_id=uuid4(),
        now=datetime.now(timezone.utc),
    )

    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"


def test_moisture_sensor_value_is_in_range():
    adapter = SimulationSensorAdapter("moisture_sensor")

    reading = adapter.read(
        device_id=uuid4(),
        now=datetime.now(timezone.utc),
    )

    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"


def test_light_sensor_value_is_in_range():
    adapter = SimulationSensorAdapter("light_sensor")

    reading = adapter.read(
        device_id=uuid4(),
        now=datetime.now(timezone.utc),
    )

    assert 200 <= reading.value <= 2000
    assert reading.unit == "lux"
    assert reading.source == "simulation"