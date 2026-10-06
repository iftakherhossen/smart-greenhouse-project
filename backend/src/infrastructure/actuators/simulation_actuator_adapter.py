import logging
from uuid import UUID

from src.domain.sensors.ports import ActuatorPort


logger = logging.getLogger(__name__)


class SimulationActuatorAdapter(ActuatorPort):
    """
    Simulation adapter for actuators.

    No real hardware is controlled. Commands are only recorded/logged.
    """

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        logger.info(
            "Simulation actuator command: device_id=%s command=%s payload=%s",
            device_id,
            command,
            payload,
        )
