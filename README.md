# Elecnova Client

Python client library for the Elecnova ECO EMS Cloud API.

**Version 0.3.0** - API V2.2.0 project → site → device hierarchy.

## Features

- 🔐 HMAC-SHA256 authentication with automatic token management
- 📦 Type-safe Pydantic models for API responses
- ⚡ Async HTTP client using httpx
- 🔄 Synchronous wrapper for non-async environments
- 🌞 Photovoltaic power generation endpoints (v1.3.1+)
- 🏗️ Project → site → device hierarchy (v2.2.0+) for durable site attribution
- 🔧 Component type standardization with official codes
- ✅ Comprehensive test coverage
- 🚀 Zero dependencies on specific frameworks (works with any Python application)

## Installation

```bash
# From PyPI (recommended)
pip install elecnova-client

# From GitHub
pip install git+https://github.com/elektriciteit-steen/elecnova-client.git

# From source (for development)
git clone https://github.com/elektriciteit-steen/elecnova-client.git
cd elecnova-client
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Migration Guide

### v0.1.5 → v0.1.6 (AUTHENTICATION FIX - NOW WORKING!)

**Version 0.1.6 includes critical authentication fixes** that make the client fully functional with the Elecnova API.

**What Changed:**
- ✅ Fixed business API authentication (raw token + all signature headers)
- ✅ Fixed MQTT subscription endpoint (GET instead of POST)
- ✅ Fixed response parsing for raw API responses
- ✅ Updated models to match actual API response format

**No code changes required** - simply upgrade to v0.1.6:

```bash
pip install --upgrade elecnova-client
```

**Verified Working:**
- ✅ Authentication (`/comm/client`)
- ✅ Get cabinets (`/api/v1/dev`) - Successfully retrieves all cabinets
- ✅ Get components (`/api/v1/dev/{sn}`) - Successfully retrieves all components
- ✅ All v1.3.1 features (`component`, `component_desc` fields)

### v0.1.4 → v0.1.5 (ENDPOINT CORRECTIONS)

**Version 0.1.5 fixed critical endpoint paths** to match official documentation:

| Method | Old (v0.1.4) | New (v0.1.5) |
|--------|--------------|--------------|
| `get_cabinets()` | `/api/v1/cabinet/list` | `/api/v1/dev` |
| `get_components()` | `/api/v1/cabinet/{sn}/components` | `/api/v1/dev/{sn}` |

## Usage

### Async Client

```python
from elecnova_client import ElecnovaClient


async def main():
    client = ElecnovaClient(client_id="your_client_id", client_secret="your_client_secret")

    # Fetch ESS cabinets (devices)
    cabinets = await client.get_cabinets(page=1, page_size=100)
    for cabinet in cabinets:
        print(f"Cabinet: {cabinet.sn} - {cabinet.name}")
        print(f"  Model: {cabinet.model}")
        print(f"  Timezone: {cabinet.time_zone}")

    # Fetch components for a specific cabinet
    components = await client.get_components(cabinet_sn="ESS123456")
    for component in components:
        print(f"Component: {component.sn}")
        print(f"  Type: {component.type}")
        print(f"  Component Code: {component.component}")  # v1.3.1+
        print(f"  Description: {component.component_desc}")  # v1.3.1+
        print(f"  State: {component.state}")

    # Subscribe to MQTT topics for real-time data
    result = await client.subscribe_mqtt_topics(device_id="123", sn="ESS123456")

    # Walk the project -> site -> device hierarchy (v2.2.0+)
    for project in await client.get_projects():
        print(f"Project: {project.name} ({project.id})")
        for site in await client.get_project_sites(project.id):
            # site.id is the same UUID as the web UI station ID: a durable join key
            print(f"  Site: {site.name} ({site.id}) {site.rated_power} kW")
            for device in await client.get_site_devices(site.id):
                # device.id matches Cabinet.id from get_cabinets()
                print(f"    Device: {device.sn} ({device.model}) id={device.id}")

    # Fetch PV power generation with 5-minute intervals (v1.3.1+)
    power_data = await client.get_pv_power_cap(
        sn="PV123456", begin="2025-11-01T00:00:00Z", end="2025-11-01T23:59:59Z"
    )
    for point in power_data:
        print(f"{point.time}: {point.value}W")

    # Get PV daily generation for past 7 days (v1.3.1+)
    daily_data = await client.get_pv_power_gen_daily(sn="PV123456")
    for point in daily_data:
        print(f"{point.time}: {point.value} kWh")

    # Get PV monthly generation (v1.3.1+)
    monthly_data = await client.get_pv_power_gen_monthly(sn="PV123456", month="2025-11")

    # Get PV yearly generation (v1.3.1+)
    yearly_data = await client.get_pv_power_gen_yearly(sn="PV123456", year="2025")

    # Always close the client when done
    await client.close()
```

### Context Manager (Recommended)

```python
async def main():
    async with ElecnovaClient(
        client_id="your_client_id", client_secret="your_client_secret"
    ) as client:
        cabinets = await client.get_cabinets()
        # Client automatically closes when exiting context
```

### Sync Client

```python
from elecnova_client import ElecnovaClientSync

client = ElecnovaClientSync(client_id="your_client_id", client_secret="your_client_secret")

# Fetch cabinets (synchronous)
cabinets = client.get_cabinets(page=1, page_size=100)
for cabinet in cabinets:
    print(f"Cabinet: {cabinet.sn} - {cabinet.name}")
```

## API Reference

### Models

#### Cabinet
ESS Cabinet (Device) data model with pagination support.

**Fields:**
- `id`: Unique device ID
- `sn`: Serial number
- `name`: Cabinet name
- `model`: Cabinet model
- `time_zone`: Installation timezone
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Component
Component (BMS, PCS, Meter, Sensors, etc.) data model.

**Fields:**
- `sn`: Component serial number (unique identifier)
- `name`: Component name
- `model`: Component model
- `type`: Component type (legacy field)
- `state`: Component state (online/offline)
- `location_code`: Location code for data point mapping
- `cabinet_sn`: Parent cabinet serial number
- `component`: Component type code [v1.3.1+] - see Component Types section
- `component_desc`: Component type description [v1.3.1+] - see Component Types section

#### Project
Top level of the hierarchy [v2.2.0+].

**Fields:**
- `id`: Project UUID
- `name`: Project name
- `code`: Project code
- `region`: Project region (may be an empty string)
- `addr`: Project address (may be an empty string)
- `begin_at`: Project start date (YYYY-MM-DD)

#### Site
Power station, the middle level of the hierarchy [v2.2.0+].

**Fields:**
- `id`: Site UUID — **the same UUID as the station ID in the Elecnova web UI**, so it is
  a durable join key for site attribution (names are not)
- `name`: Site name
- `rated_power`: Rated power (kW)
- `rated_capacity`: Rated capacity (kWh) — documented, absent from the live payload
- `time_zone`: Site timezone (e.g., `Europe/Brussels`)
- `begin_at`: Site start date — documented, absent from the live payload
- `addr`: Site address — documented, absent from the live payload

#### Device
Leaf level of the hierarchy [v2.2.0+].

**Fields:**
- `id`: Device UUID — **the same UUID as `Cabinet.id` from `GET /api/v1/dev`**, so the v2
  hierarchy joins cleanly onto the existing v1 device surface
- `sn`: Device serial number
- `name`: Device name
- `model`: Device model (e.g., `ECO-E215WS`)

#### Pagination / PaginatedV2Response
The envelope of a paginated v2 response: `{"data": [...], "pagination": {"page": 1,
"page_size": 10, "total_count": 1}}`. The API's own default `page_size` is 10, max 1000.

Note that the v2 endpoints name their fields in **snake_case** on the wire (`time_zone`,
`begin_at`, `rated_power`, `page_size`, `total_count`), unlike v1 which uses camelCase
for some fields (`timeZone`, `lastSeen`). The models follow what the API actually
returns; they do not normalise it.

#### PowerDataPoint
PV power generation data point [v1.3.1+].

**Fields:**
- `time`: Timestamp in RFC3339 format
- `value`: Power value (unit varies by endpoint)

#### TokenResponse
OAuth token response (internal use).

**Fields:**
- `id`: MQTT Client ID
- `username`: MQTT username
- `password`: MQTT password
- `token`: Bearer token (24-hour TTL)

### Component Types (v1.3.1+)

The API now provides standardized component type codes in the `component` field:

| Code | Description | Usage |
|------|-------------|-------|
| `ess.ems` | EMS | Energy Management System |
| `ess.bms` | BMS | Battery Management System |
| `ess.pcs` | PCS | Power Conversion System |
| `pv.inv` | PV | Photovoltaic Inverter |
| `ess.meter` | Meter | Energy Meter |
| `ess.battery` | Battery | Battery Pack |
| `ess.fire` | Fire Host | Fire Suppression System |
| `ess.ac` | Air Conditioning | HVAC System |

Access these via `component.component` (code) and `component.component_desc` (description).

### Client Methods

#### Authentication
- `get_token()`: Obtain/refresh access token (automatically called, 24-hour TTL)

#### Device Management
- `get_cabinets(page=1, page_size=100)`: List ESS cabinets with pagination
  - **Endpoint:** `GET /api/v1/dev`
  - **Returns:** List of `Cabinet` objects
- `get_components(cabinet_sn)`: List components for a specific cabinet
  - **Endpoint:** `GET /api/v1/dev/{sn}`
  - **Returns:** List of `Component` objects

#### Hierarchy [v2.2.0+]
- `get_projects()`: List all projects
  - **Endpoint:** `GET /api/v2/projects`
  - **Response shape:** bare JSON array (no envelope)
  - **Returns:** List of `Project` objects
- `get_project_sites(project_id, page=1, page_size=100)`: List the sites of a project
  - **Endpoint:** `GET /api/v2/project/{id}/sites`
  - **Response shape:** `{"data": [...], "pagination": {...}}`
  - **Returns:** List of `Site` objects for the requested page. A `WARNING` is logged
    when `pagination.total_count` exceeds the page requested, so a short page cannot
    silently pass for the whole set.
- `get_site_devices(site_id)`: List the devices of a site
  - **Endpoint:** `GET /api/v2/site/{id}/devices`
  - **Response shape:** bare JSON array (no envelope)
  - **Returns:** List of `Device` objects

#### MQTT Subscription
- `subscribe_mqtt_topics(device_id, sn)`: Subscribe to MQTT topics for real-time data
  - **Endpoint:** `POST /api/v1/dev/topic/{device_id}/{sn}`
  - **Returns:** Subscription result dictionary

#### PV Power Generation [v1.3.1+]
- `get_pv_power_cap(sn, begin, end)`: Get PV power generation with 5-minute intervals
  - **Endpoint:** `GET /api/v1/dev/pv/power-cap/{sn}`
  - **Params:** `begin` and `end` in RFC3339 format (e.g., "2025-11-01T00:00:00Z")
  - **Returns:** List of `PowerDataPoint` (power in watts)
- `get_pv_power_gen_daily(sn)`: Get PV daily generation for past 7 days
  - **Endpoint:** `GET /api/v1/dev/pv/power-gen/daily/{sn}`
  - **Returns:** List of `PowerDataPoint` (daily energy in kWh)
- `get_pv_power_gen_monthly(sn, month)`: Get PV monthly daily generation
  - **Endpoint:** `GET /api/v1/dev/pv/power-gen/monthly/{sn}`
  - **Params:** `month` in YYYY-MM format (e.g., "2025-11")
  - **Returns:** List of `PowerDataPoint` (daily energy for the month)
- `get_pv_power_gen_yearly(sn, year)`: Get PV annual monthly generation
  - **Endpoint:** `GET /api/v1/dev/pv/power-gen/yearly/{sn}`
  - **Params:** `year` in YYYY format (e.g., "2025")
  - **Returns:** List of `PowerDataPoint` (monthly energy for the year)

### Exception Handling

```python
from elecnova_client import (
    ElecnovaAPIError,
    ElecnovaAuthError,
    ElecnovaRateLimitError,
    ElecnovaTimeoutError,
)

try:
    cabinets = await client.get_cabinets()
except ElecnovaAuthError as e:
    print(f"Authentication failed: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
except ElecnovaRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ElecnovaTimeoutError as e:
    print(f"Request timeout: {e}")
except ElecnovaAPIError as e:
    print(f"API error: {e}")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=elecnova_client --cov-report=html

# Run linter
ruff check .

# Format code
ruff format .

# Type checking
mypy src/
```

## API Documentation

Based on **Elecnova ECO EMS Cloud API Interface Document V1.3.1**

### Authentication Flow

1. **Client Registration:** Obtain `Client ID` and `Client Secret` from Elecnova
2. **IP Whitelisting:** Provide source IP address for access approval
3. **Token Request:** Call `GET /comm/client` with HMAC-SHA256 signature
4. **Token Usage:** Include Bearer token in `Authorization` header for all API calls
5. **Token Refresh:** Automatic refresh 5 minutes before 24-hour expiry

### Technical Specifications

- **Authentication:** HMAC-SHA256 signature with Base64 encoding
- **Token Validity:** 24 hours (86400 seconds)
- **Token Refresh:** Automatic, 5 minutes before expiry
- **Rate Limit:** 100 requests/second
- **MQTT Protocol:** MQTTS (secure MQTT)
- **MQTT Port:** 1884
- **Base URL:** `https://api.elecnova.com` (configurable)
- **Timeout:** 30 seconds (configurable)

### API Endpoints (v1.3.1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/comm/client` | GET | Request authentication token and MQTT credentials |
| `/api/v1/dev` | GET | Get device list (ESS cabinets) with pagination |
| `/api/v1/dev/{sn}` | GET | Get device component information |
| `/api/v1/dev/topic/{device_id}/{sn}` | POST | Subscribe to MQTT topics |
| `/api/v1/dev/pv/power-cap/{sn}` | GET | Get PV power generation (5-min intervals) |
| `/api/v1/dev/pv/power-gen/daily/{sn}` | GET | Get PV daily generation (past 7 days) |
| `/api/v1/dev/pv/power-gen/monthly/{sn}` | GET | Get PV monthly generation |
| `/api/v1/dev/pv/power-gen/yearly/{sn}` | GET | Get PV yearly generation |

### API Endpoints (v2.2.0)

| Endpoint | Method | Response shape | Description |
|----------|--------|----------------|-------------|
| `/api/v2/projects` | GET | bare array | List projects |
| `/api/v2/project/{id}/sites` | GET | `{data, pagination}` | List a project's sites (power stations) |
| `/api/v2/site/{id}/devices` | GET | bare array | List a site's devices |

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## License

LGPL-3.0-or-later

## Support

For issues, feature requests, or contributions, please visit:
https://github.com/elektriciteit-steen/elecnova-client

## Author

Steen Elektriciteit
- Email: info@steenelektriciteit.be
- Website: https://www.steenelektriciteit.be
