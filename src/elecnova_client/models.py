"""Pydantic models for Elecnova API responses."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Cabinet(BaseModel):
    """Elecnova ESS Cabinet."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Cabinet unique ID (UUID)")
    sn: str = Field(..., description="Cabinet serial number (unique identifier)")
    name: str | None = Field(None, description="Cabinet name")
    model: str | None = Field(None, description="Cabinet model (e.g., ECO-E107WS)")
    time_zone: str | None = Field(None, alias="timeZone", description="Cabinet timezone")
    state: str | None = Field(None, description="Cabinet state (online/offline)")
    last_seen: datetime | None = Field(
        None, alias="lastSeen", description="Last communication timestamp"
    )


class Component(BaseModel):
    """Elecnova Component (BMS, PCS, Meter, Sensors, etc.)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Component unique ID")
    sn: str = Field(..., description="Component serial number (unique identifier)")
    name: str | None = Field(None, description="Component name")
    model: str | None = Field(None, description="Component model")
    type: str | None = Field(None, description="Component type")
    state: bool | None = Field(None, description="Component state (True=online, False=offline)")
    location_code: str | None = Field(
        None, alias="locationCode", description="Location code for data point mapping"
    )
    cabinet_sn: str = Field(..., alias="cabinetSn", description="Parent cabinet serial number")
    component: str | None = Field(
        None, description="Component type code (v1.3.1+): ess.ems, ess.bms, ess.pcs, pv.inv, etc."
    )
    component_desc: str | None = Field(
        None,
        alias="componentDesc",
        description="Component type description (v1.3.1+): EMS, BMS, PCS, PV, Meter",
    )


class TokenResponse(BaseModel):
    """OAuth token response."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(..., alias="accessToken", description="Bearer token")
    expires_in: int = Field(
        ..., alias="expiresIn", description="Token validity in seconds (typically 86400 = 24h)"
    )
    token_type: str = Field(default="Bearer", alias="tokenType", description="Token type")


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    model_config = ConfigDict(populate_by_name=True)

    code: int = Field(..., description="Response code (200 = success)")
    message: str = Field(..., description="Response message")
    data: T | None = Field(None, description="Response data")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response."""

    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., alias="pageSize", description="Records per page")
    records: list[T] = Field(default_factory=list, description="Page records")


class PowerDataPoint(BaseModel):
    """Power generation data point (v1.3.1+)."""

    model_config = ConfigDict(populate_by_name=True)

    time: str = Field(..., description="Timestamp in RFC3339 format")
    value: float = Field(..., description="Power value")
