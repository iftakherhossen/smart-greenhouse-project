from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ZoneConfigRequest(BaseModel):
    name: str
    moisture_threshold_low: float = Field(ge=0.0, le=1.0)
    moisture_threshold_high: float = Field(ge=0.0, le=1.0)
    schedule: dict[str, Any] = Field(default_factory=dict)


class LocationConfigRequest(BaseModel):
    location_name: str
    zones: list[ZoneConfigRequest]


class ZoneCreateRequest(BaseModel):
    name: str
    moisture_threshold_low: float = Field(ge=0.0, le=1.0)
    moisture_threshold_high: float = Field(ge=0.0, le=1.0)
    schedule: dict[str, Any] = Field(default_factory=dict)


class ZoneUpdateRequest(BaseModel):
    name: str
    moisture_threshold_low: float = Field(ge=0.0, le=1.0)
    moisture_threshold_high: float = Field(ge=0.0, le=1.0)
    schedule: dict[str, Any] = Field(default_factory=dict)


class LocationSummaryResponse(BaseModel):
    id: UUID
    name: str


class ZoneResponse(BaseModel):
    id: UUID
    location_id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict[str, Any]


class LocationConfigResponse(BaseModel):
    location: LocationSummaryResponse
    zones: list[ZoneResponse]


class DeviceZoneAssignmentRequest(BaseModel):
    zone_id: UUID | None = None