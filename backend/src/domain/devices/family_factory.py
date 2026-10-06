from abc import ABC, abstractmethod

from src.domain.devices.entity import Device
from src.domain.sensors.creators import LightSensorCreator, MoistureSensorCreator


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        """Unique identifier key for the device family."""
        ...

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        """Creates a coherent kit of 2 sensors and 2 actuators for this family."""
        ...


class SimulationDeviceFactory(DeviceFamilyFactory):
    def __init__(self) -> None:
        self._moisture_creator = MoistureSensorCreator()
        self._light_creator = LightSensorCreator()

    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        sim_moisture = self._moisture_creator.create_sensor(
            display_name="Sim Soil Moisture Sensor"
        )
        sim_light = self._light_creator.create_sensor(
            display_name="Sim Ambient Light Sensor"
        )

        sensors = [
            Device(
                device_type=sim_moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=(
                    sim_moisture.display_name
                    or "Sim Soil Moisture Sensor"
                ),
                default_config={
                    **sim_moisture.default_config,
                    "protocol": "simulation",
                },
            ),
            Device(
                device_type=sim_light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=(
                    sim_light.display_name
                    or "Sim Ambient Light Sensor"
                ),
                default_config={
                    **sim_light.default_config,
                    "protocol": "simulation",
                },
            ),
        ]

        actuators = [
            Device(
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim Irrigation Pump",
                default_config={
                    "protocol": "sim",
                    "flow_rate_lpm": 2.5,
                    "state": "off",
                },
            ),
            Device(
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim LED Grow Light",
                default_config={
                    "protocol": "sim",
                    "spectrum": "full_spectrum",
                    "intensity_pct": 0,
                },
            ),
        ]

        return sensors + actuators


class EdgeHardwareFactory(DeviceFamilyFactory):
    def __init__(self) -> None:
        self._moisture_creator = MoistureSensorCreator()
        self._light_creator = LightSensorCreator()

    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        edge_moisture = self._moisture_creator.create_sensor(
            display_name="Edge Soil Moisture Sensor"
        )
        edge_light = self._light_creator.create_sensor(
            display_name="Edge Ambient Light Sensor"
        )

        sensors = [
            Device(
                device_type=edge_moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=(
                    edge_moisture.display_name
                    or "Edge Soil Moisture Sensor"
                ),
                default_config={
                    **edge_moisture.default_config,
                    "protocol": "i2c",
                    "i2c_address": "0x36",
                    "bus": 1,
                },
            ),
            Device(
                device_type=edge_light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=(
                    edge_light.display_name
                    or "Edge Ambient Light Sensor"
                ),
                default_config={
                    **edge_light.default_config,
                    "protocol": "spi",
                    "spi_bus": 0,
                    "chip_select": 0,
                },
            ),
        ]

        actuators = [
            Device(
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge Relay Irrigation Pump",
                default_config={
                    "protocol": "gpio-relay",
                    "gpio_pin": 17,
                    "active_high": True,
                },
            ),
            Device(
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge PWM Grow Light",
                default_config={
                    "protocol": "pwm",
                    "gpio_pin": 18,
                    "frequency_hz": 1000,
                },
            ),
        ]

        return sensors + actuators


def get_family_factory(family: str) -> DeviceFamilyFactory:
    factories: dict[str, DeviceFamilyFactory] = {
        "simulation": SimulationDeviceFactory(),
        "edge": EdgeHardwareFactory(),
    }

    try:
        return factories[family]
    except KeyError:
        raise ValueError(
            f"Unknown device family: '{family}'. "
            f"Allowed families: {list(factories.keys())}"
        )