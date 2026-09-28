from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class Device:
    device_type: str
    role: str  # "sensor" | "actuator"
    device_family: str  # "simulation" | "edge"
    display_name: str
    default_config: dict = field(default_factory=dict)
    id: UUID | None = None
    zone_id: UUID | None = None
    location_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.role not in {"sensor", "actuator"}:
            raise ValueError(
                f"Invalid device role: '{self.role}'. "
                "Must be 'sensor' or 'actuator'."
            )