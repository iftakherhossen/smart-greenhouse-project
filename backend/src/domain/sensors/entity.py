from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Sensor:
    device_type: str
    display_name: str | None = None
    default_config: dict = field(default_factory=dict)
    id: UUID | None = None


@dataclass(frozen=True)
class Reading:
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        if self.source not in {"simulation", "mqtt", "vendor"}:
            raise ValueError(
                f"Invalid reading source: '{self.source}'."
            )

        if self.recorded_at.tzinfo is None:
            raise ValueError(
                "recorded_at must be timezone-aware."
            )