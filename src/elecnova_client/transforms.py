"""Transform functions to convert API models to Odoo record format."""

from typing import Any

from .models import Cabinet, Component


def transform_cabinet_to_odoo(cabinet: Cabinet) -> dict[str, Any]:
    """Transform Cabinet API model to Odoo elecnova.cabinet record format.

    Args:
        cabinet: Cabinet model from API

    Returns:
        Dictionary ready for Odoo bulk_upsert_with_sync
    """
    record = {
        "raw_sn": cabinet.sn,
        "raw_name": cabinet.name,
        "raw_model": cabinet.model,
        "raw_time_zone": cabinet.time_zone,
        "raw_state": cabinet.state,
    }

    # Add last_seen if available
    if cabinet.last_seen:
        # Convert to string format that Odoo expects
        record["raw_last_seen"] = cabinet.last_seen.strftime("%Y-%m-%d %H:%M:%S")

    return record


def transform_component_to_odoo(component: Component, cabinet_id: int | None = None) -> dict[str, Any]:
    """Transform Component API model to Odoo elecnova.component record format.

    Args:
        component: Component model from API
        cabinet_id: Optional Odoo cabinet ID (Many2one reference)

    Returns:
        Dictionary ready for Odoo bulk_upsert_with_sync
    """
    record = {
        "raw_sn": component.sn,
        "raw_name": component.name,
        "raw_model": component.model,
        "raw_type": component.type,
        "raw_state": component.state,
        "raw_location_code": component.location_code,
    }

    # Add cabinet_id if provided (Odoo Many2one)
    if cabinet_id is not None:
        record["cabinet_id"] = cabinet_id

    return record
