from src.domain.sensors.ports import SensorPort
from src.infrastructure.sensors.mqtt_adapter import MqttSensorAdapter
from src.infrastructure.sensors.simulation_adapter import SimulationSensorAdapter
from src.infrastructure.sensors.vendor_stub_adapter import VendorStubAdapter


def select_sensor_adapter(
    device_type: str,
    default_config: dict,
) -> SensorPort | MqttSensorAdapter:
    """
    Select the sensor adapter based on device configuration.

    The vendor stub uses a separate driver flag.
    Otherwise, the protocol selects the adapter.
    """

    driver = default_config.get("driver")

    if driver == "vendor_stub":
        return VendorStubAdapter(device_type)

    protocol = default_config.get("protocol")

    if protocol in {"simulation", "sim_virtual_bus"}:
        return SimulationSensorAdapter(device_type)

    if protocol == "mqtt":
        return MqttSensorAdapter()

    raise ValueError(
        f"Unsupported sensor configuration: "
        f"protocol='{protocol}', driver='{driver}'"
    )