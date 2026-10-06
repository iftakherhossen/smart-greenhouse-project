from datetime import datetime
from uuid import UUID

from src.domain.sensors.entity import Reading
from src.domain.sensors.ports import SensorPort


class VendorStubAdapter(SensorPort):
    def __init__(self, device_type: str):
        self._device_type = device_type

    def _read_vendor_payload(self) -> dict:
        if self._device_type == "moisture_sensor":
            return {
                "sensor_value": 0.42,
                "measurement_unit": "vwc",
            }

        if self._device_type == "light_sensor":
            return {
                "sensor_value": 850.0,
                "measurement_unit": "lux",
            }

        raise ValueError(
            f"Unsupported vendor sensor type: '{self._device_type}'"
        )

    def read(self, device_id: UUID, now: datetime) -> Reading:
        payload = self._read_vendor_payload()

        return Reading(
            device_id=device_id,
            value=float(payload["sensor_value"]),
            unit=payload["measurement_unit"],
            source="vendor",
            recorded_at=now,
        )