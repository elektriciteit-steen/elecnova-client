# Elecnova Client

Python client library for the Elecnova ECO EMS Cloud API.

## Features

- 🔐 HMAC-SHA256 authentication with automatic token management
- 📦 Type-safe Pydantic models for API responses
- ⚡ Async HTTP client using httpx (for Prefect)
- 🔄 Synchronous wrapper (for Odoo compatibility)
- 🔧 Transform functions for Odoo integration
- ✅ Comprehensive test coverage

## Installation

```bash
# From GitHub
pip install git+https://github.com/jwaes/elecnova-client.git

# From source (for development)
git clone https://github.com/jwaes/elecnova-client.git
cd elecnova-client
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

### Async Client (Prefect)

```python
from elecnova_client import ElecnovaClient

async def main():
    client = ElecnovaClient(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )

    # Fetch cabinets
    cabinets = await client.get_cabinets(page=1, page_size=100)

    # Fetch components for a cabinet
    components = await client.get_components(cabinet_sn="ESS123456")

    # Subscribe to MQTT topics
    result = await client.subscribe_mqtt_topics(device_id="123", sn="ESS123456")
```

### Sync Client (Odoo)

```python
from elecnova_client import ElecnovaClientSync

client = ElecnovaClientSync(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Fetch cabinets (synchronous)
cabinets = client.get_cabinets(page=1, page_size=100)
```

### Transform Functions

```python
from elecnova_client import transform_cabinet_to_odoo, transform_component_to_odoo

# Convert API models to Odoo record format
cabinet_dict = transform_cabinet_to_odoo(cabinet)
component_dict = transform_component_to_odoo(component)
```

## API Reference

### Models

- `Cabinet`: ESS Cabinet data model
- `Component`: Component (BMS, PCS, Meter, etc.) data model
- `TokenResponse`: OAuth token response
- `ApiResponse[T]`: Generic API response wrapper

### Client Methods

- `get_token()`: Obtain/refresh access token
- `get_cabinets(page, page_size)`: List cabinets with pagination
- `get_components(cabinet_sn)`: List components for a cabinet
- `subscribe_mqtt_topics(device_id, sn)`: Subscribe to MQTT topics

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

Based on Elecnova ECO EMS Cloud API Interface Document V1.2.1

- Authentication: HMAC-SHA256 with client credentials
- Token validity: 24 hours
- Rate limit: 100 requests/second
- MQTT: MQTTS protocol (port 8883)

## License

LGPL-3.0-or-later
