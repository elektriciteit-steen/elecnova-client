"""Tests for transform functions."""

from datetime import UTC, datetime

from elecnova_client.models import Cabinet, Component
from elecnova_client.transforms import transform_cabinet_to_odoo, transform_component_to_odoo


def test_transform_cabinet_to_odoo():
    """Test cabinet transformation to Odoo format."""
    cabinet = Cabinet(
        sn="ESS123456",
        name="Test Cabinet",
        model="ECO-E107WS",
        timeZone="UTC",
        state="online",
        lastSeen=datetime(2025, 10, 13, 12, 0, 0, tzinfo=UTC),
    )

    odoo_record = transform_cabinet_to_odoo(cabinet)

    assert odoo_record["raw_sn"] == "ESS123456"
    assert odoo_record["raw_name"] == "Test Cabinet"
    assert odoo_record["raw_model"] == "ECO-E107WS"
    assert odoo_record["raw_time_zone"] == "UTC"
    assert odoo_record["raw_state"] == "online"
    assert odoo_record["raw_last_seen"] == "2025-10-13 12:00:00"


def test_transform_cabinet_minimal():
    """Test cabinet transformation with minimal data."""
    cabinet = Cabinet(sn="ESS123456")

    odoo_record = transform_cabinet_to_odoo(cabinet)

    assert odoo_record["raw_sn"] == "ESS123456"
    assert odoo_record["raw_name"] is None
    assert "raw_last_seen" not in odoo_record


def test_transform_component_to_odoo():
    """Test component transformation to Odoo format."""
    component = Component(
        sn="BMS001",
        name="Battery Management System",
        model="BMS-100",
        type="bms",
        state="online",
        locationCode="bms_01",
        cabinetSn="ESS123456",
    )

    odoo_record = transform_component_to_odoo(component)

    assert odoo_record["raw_sn"] == "BMS001"
    assert odoo_record["raw_name"] == "Battery Management System"
    assert odoo_record["raw_model"] == "BMS-100"
    assert odoo_record["raw_type"] == "bms"
    assert odoo_record["raw_state"] == "online"
    assert odoo_record["raw_location_code"] == "bms_01"
    assert "cabinet_id" not in odoo_record


def test_transform_component_with_cabinet_id():
    """Test component transformation with cabinet_id."""
    component = Component(
        sn="BMS001",
        cabinetSn="ESS123456",
    )

    odoo_record = transform_component_to_odoo(component, cabinet_id=42)

    assert odoo_record["raw_sn"] == "BMS001"
    assert odoo_record["cabinet_id"] == 42
