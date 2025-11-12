"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from elecnova_client.models import Cabinet, Component, TokenResponse


def test_cabinet_model():
    """Test Cabinet model validation."""
    cabinet = Cabinet(
        id="550e8400-e29b-41d4-a716-446655440000",
        sn="ESS123456",
        name="Test Cabinet",
        model="ECO-E107WS",
        timeZone="UTC",
        state="online",
    )

    assert cabinet.id == "550e8400-e29b-41d4-a716-446655440000"
    assert cabinet.sn == "ESS123456"
    assert cabinet.name == "Test Cabinet"
    assert cabinet.model == "ECO-E107WS"
    assert cabinet.time_zone == "UTC"
    assert cabinet.state == "online"


def test_cabinet_model_minimal():
    """Test Cabinet model with minimal fields."""
    cabinet = Cabinet(id="550e8400-e29b-41d4-a716-446655440000", sn="ESS123456")
    assert cabinet.id == "550e8400-e29b-41d4-a716-446655440000"
    assert cabinet.sn == "ESS123456"
    assert cabinet.name is None


def test_cabinet_model_missing_sn():
    """Test Cabinet model validation fails without required field."""
    with pytest.raises(ValidationError):
        Cabinet(name="Test Cabinet")


def test_component_model():
    """Test Component model validation."""
    component = Component(
        id="660e8400-e29b-41d4-a716-446655440000",
        sn="BMS001",
        name="Battery Management System",
        model="BMS-100",
        type="bms",
        state=True,
        locationCode="bms_01",
        cabinetSn="ESS123456",
    )

    assert component.id == "660e8400-e29b-41d4-a716-446655440000"
    assert component.sn == "BMS001"
    assert component.name == "Battery Management System"
    assert component.model == "BMS-100"
    assert component.type == "bms"
    assert component.state is True
    assert component.location_code == "bms_01"
    assert component.cabinet_sn == "ESS123456"


def test_component_model_minimal():
    """Test Component model with minimal fields."""
    component = Component(
        id="660e8400-e29b-41d4-a716-446655440000",
        sn="BMS001",
        cabinetSn="ESS123456",
    )
    assert component.id == "660e8400-e29b-41d4-a716-446655440000"
    assert component.sn == "BMS001"
    assert component.cabinet_sn == "ESS123456"
    assert component.name is None


def test_token_response_model():
    """Test TokenResponse model validation."""
    token = TokenResponse(
        accessToken="test_token_12345",
        expiresIn=86400,
        tokenType="Bearer",
    )

    assert token.access_token == "test_token_12345"
    assert token.expires_in == 86400
    assert token.token_type == "Bearer"
