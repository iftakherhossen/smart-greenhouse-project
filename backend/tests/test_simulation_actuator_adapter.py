from uuid import uuid4

from src.infrastructure.actuators.simulation_actuator_adapter import (
    SimulationActuatorAdapter,
)


def test_simulation_actuator_accepts_command():
    adapter = SimulationActuatorAdapter()

    device_id = uuid4()

    result = adapter.apply(
        device_id=device_id,
        command="turn_on",
        payload={"power": 100},
    )

    assert result is None