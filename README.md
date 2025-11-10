# Elecnova Client

Python client library for the Elecnova ECO EMS Cloud API.

**Version 0.1.2** - Updated for API v1.3.1 with photovoltaic power generation support.

## Features

- 🔐 HMAC-SHA256 authentication with automatic token management
- 📦 Type-safe Pydantic models for API responses
- ⚡ Async HTTP client using httpx
- 🔄 Synchronous wrapper for non-async environments
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

## Usage

### Async Client

```python
from elecnova_client import ElecnovaClient

async def main():
    client = ElecnovaClient(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )

    # Fetch cabinets
    cabinets = await client.get_cabinets(page=1, page_size=100)
    for cabinet in cabinets:
        print(f"Cabinet: {cabinet.sn} - {cabinet.name}")

    # Fetch components for a cabinet
    components = await client.get_components(cabinet_sn="ESS123456")
    for component in components:
        print(f"Component: {component.sn} ({component.type})")

    # Subscribe to MQTT topics
    result = await client.subscribe_mqtt_topics(device_id="123", sn="ESS123456")

    # Fetch PV power generation (v1.3.1+)
    power_data = await client.get_pv_power_cap(
        sn="PV123456",
        begin="2025-11-01T00:00:00Z",
        end="2025-11-01T23:59:59Z"
    )
    for point in power_data:
        print(f"{point.time}: {point.value}W")
```

### Sync Client

```python
from elecnova_client import ElecnovaClientSync

client = ElecnovaClientSync(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Fetch cabinets (synchronous)
cabinets = client.get_cabinets(page=1, page_size=100)
for cabinet in cabinets:
    print(f"Cabinet: {cabinet.sn} - {cabinet.name}")
```

## API Reference

### Models

- `Cabinet`: ESS Cabinet data model
- `Component`: Component (BMS, PCS, Meter, etc.) data model with optional `component` and `component_desc` fields [v1.3.1+]
- `TokenResponse`: OAuth token response
- `PowerDataPoint`: PV power generation data point [v1.3.1+]
- `ApiResponse[T]`: Generic API response wrapper

### Client Methods

- `get_token()`: Obtain/refresh access token
- `get_cabinets(page, page_size)`: List cabinets with pagination
- `get_components(cabinet_sn)`: List components for a cabinet
- `subscribe_mqtt_topics(device_id, sn)`: Subscribe to MQTT topics
- `get_pv_power_cap(sn, begin, end)`: Get PV power generation (5-minute intervals) [v1.3.1+]
- `get_pv_power_gen_daily(sn)`: Get PV daily generation (past 7 days) [v1.3.1+]
- `get_pv_power_gen_monthly(sn, month)`: Get PV monthly daily generation [v1.3.1+]
- `get_pv_power_gen_yearly(sn, year)`: Get PV annual monthly generation [v1.3.1+]

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Format code
ruff format .
```

## API Documentation

Based on Elecnova ECO EMS Cloud API Interface Document V1.3.1

- Authentication: GET /comm/client with Base64-encoded HMAC-SHA256 signature
- Token validity: 24 hours
- Rate limit: 100 requests/second
- MQTT: MQTTS protocol (port 1884)

## License

LGPL-3.0-or-later
