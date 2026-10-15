"""Tests for the v2 project -> site -> device hierarchy endpoints (API v2.2.0+).

The response samples below are the actual payloads returned by
https://third.elecnova-ess.com on 2026-10-15; the keys are pinned on purpose. Two of
the three endpoints answer with a bare JSON array and one with a
``{"data": ..., "pagination": ...}`` envelope, so a client that assumes the wrong shape
silently returns nothing — hence a test per shape.

All HTTP is stubbed: these tests never touch the live API.
"""

import pytest

from elecnova_client import ElecnovaClient, ElecnovaClientSync
from elecnova_client.models import Device, PaginatedV2Response, Project, Site

BASE_URL = "https://third.elecnova-ess.com"

# Bare array, exactly as GET /api/v2/projects returns it
PROJECTS_RESPONSE = [
    {
        "id": "14caa0be-8ebe-4ea3-b137-23d2df05e4c9",
        "name": "Sisa",
        "code": "1777279534083",
        "region": "",
        "addr": "",
        "begin_at": "2026-04-27",
    }
]

# Wrapped with pagination, exactly as GET /api/v2/project/{id}/sites returns it
SITES_RESPONSE = {
    "data": [
        {
            "rated_power": 100,
            "id": "7e9a0a7d-aab0-4714-9e54-317d1f593ac3",
            "name": "Sisa",
            "time_zone": "Europe/Brussels",
        }
    ],
    "pagination": {"page": 1, "page_size": 10, "total_count": 1},
}

# Bare array, exactly as GET /api/v2/site/{id}/devices returns it
DEVICES_RESPONSE = [
    {
        "id": "a25c71a2-7ba7-49c2-938f-b0219a9efe66",
        "sn": "2556110023",
        "name": "1-1 Sisa",
        "model": "ECO-E215WS",
    }
]

PROJECT_ID = "14caa0be-8ebe-4ea3-b137-23d2df05e4c9"
SITE_ID = "7e9a0a7d-aab0-4714-9e54-317d1f593ac3"

TOKEN_RESPONSE = {
    "id": "mqtt-client-id",
    "username": "mqtt-user",
    "password": "mqtt-pass",
    "token": "test-token",
}


@pytest.fixture
def stub_token(httpx_mock):
    """Stub the /comm/client token handshake every authenticated call performs."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/comm/client",
        json=TOKEN_RESPONSE,
        is_reusable=True,
    )


@pytest.fixture
def client():
    """Async client pointed at the stubbed base URL."""
    return ElecnovaClient(
        client_id="test-access-id",
        client_secret="test-secret",
        base_url=BASE_URL,
    )


# --------------------------------------------------------------------------- models


def test_project_model_parses_live_keys():
    """Project parses the live key set, snake_case, without aliases."""
    project = Project.model_validate(PROJECTS_RESPONSE[0])

    assert project.id == "14caa0be-8ebe-4ea3-b137-23d2df05e4c9"
    assert project.name == "Sisa"
    assert project.code == "1777279534083"
    assert project.region == ""
    assert project.addr == ""
    assert project.begin_at == "2026-04-27"


def test_site_model_parses_live_keys():
    """Site parses the live key set; time_zone is snake_case here, unlike v1 timeZone."""
    site = Site.model_validate(SITES_RESPONSE["data"][0])

    assert site.id == "7e9a0a7d-aab0-4714-9e54-317d1f593ac3"
    assert site.name == "Sisa"
    assert site.rated_power == 100
    assert site.time_zone == "Europe/Brussels"
    # Documented but absent from the live payload
    assert site.rated_capacity is None
    assert site.begin_at is None
    assert site.addr is None


def test_site_model_rejects_camel_case_time_zone():
    """v2 is snake_case: a camelCase timeZone key must not silently populate time_zone."""
    site = Site.model_validate({"id": SITE_ID, "timeZone": "Europe/Brussels"})
    assert site.time_zone is None


def test_device_model_parses_live_keys():
    """Device parses the live key set."""
    device = Device.model_validate(DEVICES_RESPONSE[0])

    assert device.id == "a25c71a2-7ba7-49c2-938f-b0219a9efe66"
    assert device.sn == "2556110023"
    assert device.name == "1-1 Sisa"
    assert device.model == "ECO-E215WS"


def test_paginated_v2_response_pins_pagination_keys():
    """The v2 envelope is {data, pagination{page,page_size,total_count}}."""
    paginated = PaginatedV2Response[Site].model_validate(SITES_RESPONSE)

    assert len(paginated.data) == 1
    assert paginated.pagination is not None
    assert paginated.pagination.page == 1
    assert paginated.pagination.page_size == 10
    assert paginated.pagination.total_count == 1


# ------------------------------------------------------------------- async endpoints


async def test_get_projects(client, stub_token, httpx_mock):
    """GET /api/v2/projects returns a bare array and parses into Projects."""
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/projects", json=PROJECTS_RESPONSE)

    projects = await client.get_projects()

    assert len(projects) == 1
    assert projects[0].id == PROJECT_ID
    assert projects[0].name == "Sisa"
    await client.close()


async def test_get_projects_sends_auth_headers(client, stub_token, httpx_mock):
    """The hierarchy endpoints use the existing X-Access-ID + Authorization pattern."""
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/projects", json=PROJECTS_RESPONSE)

    await client.get_projects()

    request = [r for r in httpx_mock.get_requests() if r.url.path == "/api/v2/projects"][0]
    assert request.headers["Authorization"] == "test-token"
    assert request.headers["X-Access-ID"] == "test-access-id"
    assert request.headers["X-Timestamp"]
    assert request.headers["X-Signature"]
    await client.close()


async def test_get_projects_handles_unexpected_envelope(client, stub_token, httpx_mock):
    """A wrapped payload on a bare-array endpoint yields [] rather than an exception."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/projects",
        json={"code": 200, "message": "ok", "data": PROJECTS_RESPONSE},
    )

    assert await client.get_projects() == []
    await client.close()


async def test_get_project_sites(client, stub_token, httpx_mock):
    """GET /api/v2/project/{id}/sites unwraps the {data, pagination} envelope."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/project/{PROJECT_ID}/sites?page=1&page_size=100",
        json=SITES_RESPONSE,
    )

    sites = await client.get_project_sites(PROJECT_ID)

    assert len(sites) == 1
    assert sites[0].id == SITE_ID
    assert sites[0].time_zone == "Europe/Brussels"
    assert sites[0].rated_power == 100
    await client.close()


async def test_get_project_sites_passes_pagination_params(client, stub_token, httpx_mock):
    """page / page_size are passed through as snake_case query params."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/project/{PROJECT_ID}/sites?page=2&page_size=1000",
        json={"data": [], "pagination": {"page": 2, "page_size": 1000, "total_count": 1}},
    )

    assert await client.get_project_sites(PROJECT_ID, page=2, page_size=1000) == []
    await client.close()


async def test_get_project_sites_warns_when_more_pages_remain(
    client, stub_token, httpx_mock, caplog
):
    """A page that does not cover total_count must not look like the whole truth."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/project/{PROJECT_ID}/sites?page=1&page_size=2",
        json={
            "data": SITES_RESPONSE["data"] * 2,
            "pagination": {"page": 1, "page_size": 2, "total_count": 5},
        },
    )

    with caplog.at_level("WARNING"):
        sites = await client.get_project_sites(PROJECT_ID, page=1, page_size=2)

    assert len(sites) == 2
    assert "5 sites" in caplog.text
    await client.close()


async def test_get_project_sites_handles_bare_array(client, stub_token, httpx_mock):
    """A bare array on the wrapped endpoint yields [] rather than an exception."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/project/{PROJECT_ID}/sites?page=1&page_size=100",
        json=SITES_RESPONSE["data"],
    )

    assert await client.get_project_sites(PROJECT_ID) == []
    await client.close()


async def test_get_site_devices(client, stub_token, httpx_mock):
    """GET /api/v2/site/{id}/devices returns a bare array and parses into Devices."""
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/site/{SITE_ID}/devices", json=DEVICES_RESPONSE)

    devices = await client.get_site_devices(SITE_ID)

    assert len(devices) == 1
    assert devices[0].id == "a25c71a2-7ba7-49c2-938f-b0219a9efe66"
    assert devices[0].sn == "2556110023"
    assert devices[0].model == "ECO-E215WS"
    await client.close()


async def test_get_site_devices_handles_unexpected_envelope(client, stub_token, httpx_mock):
    """A wrapped payload on a bare-array endpoint yields [] rather than an exception."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/site/{SITE_ID}/devices",
        json={"code": 200, "message": "ok", "data": DEVICES_RESPONSE},
    )

    assert await client.get_site_devices(SITE_ID) == []
    await client.close()


async def test_device_id_joins_v1_cabinet_id(client, stub_token, httpx_mock):
    """device.id is the same UUID as Cabinet.id from /api/v1/dev: the join key."""
    device_id = "a25c71a2-7ba7-49c2-938f-b0219a9efe66"
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/site/{SITE_ID}/devices", json=DEVICES_RESPONSE)
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v1/dev?page=1&pageSize=100",
        json=[
            {
                "id": device_id,
                "sn": "2556110023",
                "name": "1-1 Sisa",
                "model": "ECO-E215WS",
                "timeZone": "Europe/Brussels",
            }
        ],
    )

    devices = await client.get_site_devices(SITE_ID)
    cabinets = await client.get_cabinets()

    assert devices[0].id == cabinets[0].id
    await client.close()


# -------------------------------------------------------------------- sync endpoints


def test_sync_get_projects(stub_token, httpx_mock):
    """The sync wrapper delegates get_projects() to the async client."""
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/projects", json=PROJECTS_RESPONSE)

    with ElecnovaClientSync(
        client_id="test-access-id", client_secret="test-secret", base_url=BASE_URL
    ) as sync_client:
        projects = sync_client.get_projects()

    assert len(projects) == 1
    assert projects[0].name == "Sisa"


def test_sync_get_project_sites(stub_token, httpx_mock):
    """The sync wrapper delegates get_project_sites(), pagination args included."""
    httpx_mock.add_response(
        url=f"{BASE_URL}/api/v2/project/{PROJECT_ID}/sites?page=1&page_size=10",
        json=SITES_RESPONSE,
    )

    with ElecnovaClientSync(
        client_id="test-access-id", client_secret="test-secret", base_url=BASE_URL
    ) as sync_client:
        sites = sync_client.get_project_sites(PROJECT_ID, page=1, page_size=10)

    assert len(sites) == 1
    assert sites[0].id == SITE_ID


def test_sync_get_site_devices(stub_token, httpx_mock):
    """The sync wrapper delegates get_site_devices() to the async client."""
    httpx_mock.add_response(url=f"{BASE_URL}/api/v2/site/{SITE_ID}/devices", json=DEVICES_RESPONSE)

    with ElecnovaClientSync(
        client_id="test-access-id", client_secret="test-secret", base_url=BASE_URL
    ) as sync_client:
        devices = sync_client.get_site_devices(SITE_ID)

    assert len(devices) == 1
    assert devices[0].sn == "2556110023"
