from abc import ABC, abstractmethod

from src.domain.sensors.entity import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        ...


class MoistureSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            device_type="moisture_sensor",
            display_name=display_name,
            default_config={
                "sampling_interval_seconds": 300,
                "unit": "vwc",
                "threshold": 30,
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            device_type="light_sensor",
            display_name=display_name,
            default_config={
                "sampling_interval_seconds": 60,
                "unit": "lux",
                "threshold": 500,
            },
        )


def get_creator(sensor_type: str) -> SensorCreator:
    creators = {
        "moisture": MoistureSensorCreator(),
        "light": LightSensorCreator(),
    }

    try:
        return creators[sensor_type]
    except KeyError:
        raise ValueError(f"Unknown sensor type: {sensor_type}")