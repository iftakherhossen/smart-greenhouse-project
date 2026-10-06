import random
from datetime import datetime
from uuid import UUID

from src.domain.sensors.entity import Reading
from src.domain.sensors.ports import SensorPort


class SimulationSensorAdapter(SensorPort):
    def __init__(self, device_type: str):
        self._device_type = device_type

    def read(self, device_id: UUID, now: datetime) -> Reading:
        if self._device_type in {"moisture_sensor", "soil_moisture"}:
            value = random.uniform(0.2, 0.6)
            unit = "vwc"

        elif self._device_type in {"light_sensor", "light"}:
            value = random.uniform(200, 2000)
            unit = "lux"

        else:
            raise ValueError(
                f"Unsupported simulation sensor type: '{self._device_type}'"
            )

        return Reading(
            device_id=device_id,
            value=value,
            unit=unit,
            source="simulation",
            recorded_at=now,
        )