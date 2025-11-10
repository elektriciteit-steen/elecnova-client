"""Async HTTP client for Elecnova API."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from .exceptions import (
    ElecnovaAPIError,
    ElecnovaAuthError,
    ElecnovaRateLimitError,
    ElecnovaTimeoutError,
)
from .models import (
    ApiResponse,
    Cabinet,
    Component,
    PaginatedResponse,
    PowerDataPoint,
)

logger = logging.getLogger(__name__)


class ElecnovaClient:
    """Async HTTP client for Elecnova ECO EMS Cloud API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.elecnova.com",
        timeout: float = 30.0,
    ):
        """Initialize Elecnova API client.

        Args:
            client_id: Client ID from Elecnova
            client_secret: Client secret from Elecnova
            base_url: API base URL (default: https://api.elecnova.com)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._http_client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        requires_auth: bool = True,
        **kwargs: Any,
    ) -> dict:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., /api/v1/cabinet/list)
            requires_auth: Whether to include Bearer token (default: True)
            **kwargs: Additional arguments for httpx.request

        Returns:
            Response JSON as dictionary

        Raises:
            ElecnovaAuthError: Authentication failed
            ElecnovaRateLimitError: Rate limit exceeded
            ElecnovaTimeoutError: Request timeout
            ElecnovaAPIError: Other API errors
        """
        client = await self._get_http_client()
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})

        # Add auth token if required
        if requires_auth:
            token = await self.get_token()
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs,
            )

            # Check for rate limiting
            if response.status_code == 429:
                raise ElecnovaRateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status_code,
                    response=response.json() if response.content else None,
                )

            # Check for auth errors
            if response.status_code == 401:
                # Clear cached token and retry once
                self._token = None
                self._token_expires_at = None
                raise ElecnovaAuthError(
                    "Authentication failed",
                    status_code=response.status_code,
                    response=response.json() if response.content else None,
                )

            # Raise for other HTTP errors
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Check API response code
            if isinstance(data, dict) and data.get("code") != 200:
                raise ElecnovaAPIError(
                    f"API error: {data.get('message', 'Unknown error')}",
                    status_code=data.get("code"),
                    response=data,
                )

            return data

        except httpx.TimeoutException as e:
            raise ElecnovaTimeoutError(f"Request timeout: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ElecnovaAPIError(
                f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e

    async def get_token(self) -> str:
        """Get or refresh access token.

        Tokens are valid for 24 hours. This method caches the token and
        automatically refreshes it when it expires.

        Returns:
            Bearer token string

        Raises:
            ElecnovaAuthError: Failed to obtain token
        """
        # Return cached token if still valid
        if self._token and self._token_expires_at:
            now = datetime.now(UTC)
            # Refresh 5 minutes before expiry
            if now < (self._token_expires_at - timedelta(minutes=5)):
                return self._token

        # Request new token using /comm/client endpoint
        logger.info("Requesting new access token from /comm/client")

        # Generate timestamp and signature for /comm/client endpoint
        from .auth import generate_comm_client_signature, generate_timestamp

        timestamp = generate_timestamp()
        path = "/comm/client"
        signature = generate_comm_client_signature(path, self.client_secret, timestamp)

        # Build headers for /comm/client endpoint
        auth_headers = {
            "X-Access-ID": self.client_id,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }

        # Use GET method for /comm/client endpoint
        client = await self._get_http_client()
        url = f"{self.base_url}{path}"

        try:
            response = await client.get(url, headers=auth_headers)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise ElecnovaAuthError(f"Authentication failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise ElecnovaAuthError(f"Authentication request failed: {e}")

        # Extract token from response
        # Response format: {"id": "...", "username": "...", "password": "...", "token": "..."}
        if "token" not in data:
            raise ElecnovaAuthError(f"No token in response: {data}")

        self._token = data["token"]
        # Token expires in 24 hours (86400 seconds) according to API docs
        self._token_expires_at = datetime.now(UTC) + timedelta(seconds=86400)

        logger.info(f"Token obtained, expires at {self._token_expires_at}")
        return self._token

    async def get_cabinets(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> list[Cabinet]:
        """Fetch ESS cabinets with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of records per page (max 100)

        Returns:
            List of Cabinet objects
        """
        logger.info(f"Fetching cabinets page {page} (size: {page_size})")

        response = await self._request(
            method="GET",
            endpoint="/api/v1/cabinet/list",
            params={"page": page, "pageSize": page_size},
        )

        api_response = ApiResponse[PaginatedResponse[Cabinet]].model_validate(response)
        if not api_response.data:
            return []

        cabinets = api_response.data.records
        logger.info(f"Retrieved {len(cabinets)} cabinets (total: {api_response.data.total})")
        return cabinets

    async def get_components(self, cabinet_sn: str) -> list[Component]:
        """Fetch components for a specific cabinet.

        Args:
            cabinet_sn: Cabinet serial number

        Returns:
            List of Component objects
        """
        logger.info(f"Fetching components for cabinet {cabinet_sn}")

        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/cabinet/{cabinet_sn}/components",
        )

        api_response = ApiResponse[list[Component]].model_validate(response)
        if not api_response.data:
            return []

        components = api_response.data
        logger.info(f"Retrieved {len(components)} components for cabinet {cabinet_sn}")
        return components

    async def subscribe_mqtt_topics(self, device_id: str, sn: str) -> dict:
        """Subscribe to MQTT topics for a device.

        Must be called before connecting to MQTT broker to receive real-time data.

        Args:
            device_id: Device ID
            sn: Device serial number

        Returns:
            Subscription result dictionary
        """
        logger.info(f"Subscribing to MQTT topics for device {sn}")

        response = await self._request(
            method="POST",
            endpoint=f"/api/v1/dev/topic/{device_id}/{sn}",
        )

        logger.info(f"MQTT subscription successful for device {sn}")
        return response

    async def get_pv_power_cap(self, sn: str, begin: str, end: str) -> list[PowerDataPoint]:
        """Get PV power generation with 5-minute intervals (v1.3.1+).

        Args:
            sn: PV equipment serial number
            begin: Start time in RFC3339 format (e.g., "2025-11-01T00:00:00Z")
            end: End time in RFC3339 format (e.g., "2025-11-01T23:59:59Z")

        Returns:
            List of power data points with 5-minute intervals
        """
        logger.info(f"Fetching PV power capacity for {sn} from {begin} to {end}")

        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/dev/pv/power-cap/{sn}",
            params={"begin": begin, "end": end},
        )

        api_response = ApiResponse[list[PowerDataPoint]].model_validate(response)
        if not api_response.data:
            return []

        logger.info(f"Retrieved {len(api_response.data)} power data points")
        return api_response.data

    async def get_pv_power_gen_daily(self, sn: str) -> list[PowerDataPoint]:
        """Get PV daily power generation for the past 7 days (v1.3.1+).

        Args:
            sn: PV equipment serial number

        Returns:
            List of daily power generation data points for the past 7 days
        """
        logger.info(f"Fetching PV daily power generation for {sn}")

        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/dev/pv/power-gen/daily/{sn}",
        )

        api_response = ApiResponse[list[PowerDataPoint]].model_validate(response)
        if not api_response.data:
            return []

        logger.info(f"Retrieved {len(api_response.data)} daily power data points")
        return api_response.data

    async def get_pv_power_gen_monthly(self, sn: str, month: str) -> list[PowerDataPoint]:
        """Get PV monthly daily power generation (v1.3.1+).

        Args:
            sn: PV equipment serial number
            month: Month in YYYY-MM format (e.g., "2025-11")

        Returns:
            List of daily power generation data points for the specified month
        """
        logger.info(f"Fetching PV monthly power generation for {sn} in {month}")

        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/dev/pv/power-gen/monthly/{sn}",
            params={"month": month},
        )

        api_response = ApiResponse[list[PowerDataPoint]].model_validate(response)
        if not api_response.data:
            return []

        logger.info(f"Retrieved {len(api_response.data)} daily power data points for month")
        return api_response.data

    async def get_pv_power_gen_yearly(self, sn: str, year: str) -> list[PowerDataPoint]:
        """Get PV annual monthly power generation (v1.3.1+).

        Args:
            sn: PV equipment serial number
            year: Year in YYYY format (e.g., "2025")

        Returns:
            List of monthly power generation data points for the specified year
        """
        logger.info(f"Fetching PV yearly power generation for {sn} in {year}")

        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/dev/pv/power-gen/yearly/{sn}",
            params={"year": year},
        )

        api_response = ApiResponse[list[PowerDataPoint]].model_validate(response)
        if not api_response.data:
            return []

        logger.info(f"Retrieved {len(api_response.data)} monthly power data points for year")
        return api_response.data
