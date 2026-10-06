from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.infrastructure.sensors.vendor_stub_adapter import VendorStubAdapter


def test_vendor_moisture_reading():
    adapter = VendorStubAdapter("moisture_sensor")

    reading = adapter.read(
        device_id=uuid4(),
        now=datetime.now(timezone.utc),
    )

    assert reading.value == 0.42
    assert reading.unit == "vwc"
    assert reading.source == "vendor"


def test_vendor_light_reading():
    adapter = VendorStubAdapter("light_sensor")

    reading = adapter.read(
        device_id=uuid4(),
        now=datetime.now(timezone.utc),
    )

    assert reading.value == 850.0
    assert reading.unit == "lux"
    assert reading.source == "vendor"


def test_vendor_rejects_unsupported_sensor():
    adapter = VendorStubAdapter("unknown_sensor")

    with pytest.raises(ValueError, match="Unsupported vendor sensor type"):
        adapter.read(
            device_id=uuid4(),
            now=datetime.now(timezone.utc),
        )