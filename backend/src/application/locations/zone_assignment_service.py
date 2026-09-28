from uuid import UUID

from src.infrastructure.persistence.device_repository import DeviceRepository


class ZoneAssignmentService:
    def __init__(self, repository: DeviceRepository) -> None:
        self.repository = repository

    def assign_device(
        self,
        device_id: UUID,
        zone_id: UUID,
    ):
        device = self.repository.get_device_row(device_id)

        if device is None:
            raise ValueError("Device not found.")

        zone = self.repository.get_zone_row(zone_id)

        if zone is None:
            raise ValueError("Zone not found.")

        return self.repository.assign_device_to_zone(
            device_row=device,
            zone_row=zone,
        )

    def unassign_device(
        self,
        device_id: UUID,
    ):
        device = self.repository.get_device_row(device_id)

        if device is None:
            raise ValueError("Device not found.")

        return self.repository.unassign_device_from_zone(
            device_row=device,
        )