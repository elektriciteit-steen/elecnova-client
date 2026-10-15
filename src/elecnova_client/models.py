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


class Project(BaseModel):
    """Elecnova Project: top level of the v2 hierarchy (v2.2.0+).

    Returned by ``GET /api/v2/projects`` as a bare JSON array (no ``{code,message,data}``
    envelope). The v2 endpoints name their fields in snake_case on the wire, so no
    aliases are needed here (unlike :class:`Cabinet`, whose v1 payload is camelCase).
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Project unique ID (UUID)")
    name: str | None = Field(None, description="Project name")
    code: str | None = Field(None, description="Project code")
    region: str | None = Field(None, description="Project region (may be an empty string)")
    addr: str | None = Field(None, description="Project address (may be an empty string)")
    begin_at: str | None = Field(None, description="Project start date (YYYY-MM-DD)")


class Site(BaseModel):
    """Elecnova Site (power station): middle level of the v2 hierarchy (v2.2.0+).

    Returned by ``GET /api/v2/project/{id}/sites`` inside a
    :class:`PaginatedV2Response` envelope.

    ``id`` is the same UUID as the station ID in the Elecnova web UI, which makes it a
    durable join key for site attribution (names are not).
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Site unique ID (UUID); same as the web UI station ID")
    name: str | None = Field(None, description="Site name")
    rated_power: float | None = Field(None, description="Rated power (kW)")
    rated_capacity: float | None = Field(None, description="Rated capacity (kWh)")
    time_zone: str | None = Field(None, description="Site timezone (e.g., Europe/Brussels)")
    begin_at: str | None = Field(None, description="Site start date (YYYY-MM-DD)")
    addr: str | None = Field(None, description="Site address")


class Device(BaseModel):
    """Elecnova Device: leaf level of the v2 hierarchy (v2.2.0+).

    Returned by ``GET /api/v2/site/{id}/devices`` as a bare JSON array.

    ``id`` is the same UUID as :attr:`Cabinet.id` from ``GET /api/v1/dev``, so the v2
    hierarchy joins cleanly onto the existing v1 surface.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Device unique ID (UUID); same as Cabinet.id in /api/v1/dev")
    sn: str = Field(..., description="Device serial number")
    name: str | None = Field(None, description="Device name")
    model: str | None = Field(None, description="Device model (e.g., ECO-E215WS)")


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


class Pagination(BaseModel):
    """Pagination metadata of a v2 response (v2.2.0+)."""

    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Records per page (API default 10, max 1000)")
    total_count: int = Field(..., description="Total number of records across all pages")


class PaginatedV2Response(BaseModel, Generic[T]):
    """Envelope of a paginated v2 response: ``{"data": [...], "pagination": {...}}``.

    Distinct from :class:`PaginatedResponse` (``total``/``page``/``pageSize``/``records``)
    and from :class:`ApiResponse` (``code``/``message``/``data``): the v2 endpoints use
    their own envelope, and only some of them use an envelope at all.
    """

    model_config = ConfigDict(populate_by_name=True)

    data: list[T] = Field(default_factory=list, description="Page records")
    pagination: Pagination | None = Field(None, description="Pagination metadata")


class PowerDataPoint(BaseModel):
    """Power generation data point (v1.3.1+)."""

    model_config = ConfigDict(populate_by_name=True)

    time: str = Field(..., description="Timestamp in RFC3339 format")
    value: float = Field(..., description="Power value")
