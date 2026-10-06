from datetime import datetime, timezone
from uuid import UUID

import pytest

from src.infrastructure.sensors.mqtt_adapter import MqttSensorAdapter


DEVICE_ID = UUID("95d03d55-fee6-45c5-ad2b-0caa07ad3536")


def test_mqtt_translates_payload_to_reading():
    adapter = MqttSensorAdapter()
    now = datetime.now(timezone.utc)

    reading = adapter.translate(
        device_id=DEVICE_ID,
        payload={"value": 0.42, "unit": "vwc"},
        now=now,
    )

    assert reading.device_id == DEVICE_ID
    assert reading.value == 0.42
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"
    assert reading.recorded_at == now


def test_mqtt_rejects_missing_value():
    adapter = MqttSensorAdapter()
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError, match="missing 'value'"):
        adapter.translate(
            device_id=DEVICE_ID,
            payload={"unit": "vwc"},
            now=now,
        )


def test_mqtt_rejects_missing_unit():
    adapter = MqttSensorAdapter()
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError, match="missing 'unit'"):
        adapter.translate(
            device_id=DEVICE_ID,
            payload={"value": 0.42},
            now=now,
        )