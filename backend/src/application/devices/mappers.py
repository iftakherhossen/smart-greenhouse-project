from datetime import datetime, timezone
from src.application.devices.dto import DeviceDto
from src.domain.devices.entity import Device


def device_to_dto(entity: Device) -> DeviceDto:
    # Use getattr so missing created_at attribute does not crash
    created_val = getattr(entity, "created_at", None)
    if isinstance(created_val, datetime):
        iso_created = created_val.isoformat()
    elif isinstance(created_val, str) and created_val:
        iso_created = created_val
    else:
        iso_created = datetime.now(timezone.utc).isoformat()

    return DeviceDto(
        id=entity.id,
        device_type=entity.device_type,
        role=entity.role,
        device_family=entity.device_family,
        display_name=entity.display_name,
        default_config=entity.default_config,
        created_at=iso_created,
    )


def devices_to_dtos(entities: list[Device]) -> list[DeviceDto]:
    return [device_to_dto(e) for e in entities]
