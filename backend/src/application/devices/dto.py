from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: Literal["sensor", "actuator"]
    device_family: str
    display_name: str
    default_config: dict

    model_config = ConfigDict(from_attributes=True)
