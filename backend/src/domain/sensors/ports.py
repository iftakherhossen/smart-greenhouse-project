from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.sensors.entity import Reading


class SensorPort(ABC):
    @abstractmethod
    def read(self, device_id: UUID, now: datetime) -> Reading:
        """Read a sensor and return a normalized Reading."""
        raise NotImplementedError


class ActuatorPort(ABC):
    @abstractmethod
    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        """Apply a command to an actuator."""
        raise NotImplementedError