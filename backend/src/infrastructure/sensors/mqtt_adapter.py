from datetime import datetime
from uuid import UUID

from src.domain.sensors.entity import Reading


class MqttSensorAdapter:
    def translate(
        self,
        device_id: UUID,
        payload: dict,
        now: datetime,
    ) -> Reading:
        if "value" not in payload:
            raise ValueError("MQTT payload is missing 'value'")

        if "unit" not in payload:
            raise ValueError("MQTT payload is missing 'unit'")

        return Reading(
            device_id=device_id,
            value=float(payload["value"]),
            unit=str(payload["unit"]),
            source="mqtt",
            recorded_at=now,
        )