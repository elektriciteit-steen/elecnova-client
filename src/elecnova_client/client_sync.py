"""Synchronous wrapper for Elecnova API client (for Odoo compatibility)."""

import asyncio
from typing import Any

from .client import ElecnovaClient
from .models import Cabinet, Component, Device, Project, Site


class ElecnovaClientSync:
    """Synchronous wrapper for ElecnovaClient.

    This wrapper allows using the async client in synchronous contexts like Odoo.
    All async methods are wrapped to run in an event loop using asyncio.run().
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.elecnova.com",
        timeout: float = 30.0,
    ):
        """Initialize synchronous Elecnova API client.

        Args:
            client_id: Client ID from Elecnova
            client_secret: Client secret from Elecnova
            base_url: API base URL (default: https://api.elecnova.com)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self._async_client = ElecnovaClient(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            timeout=timeout,
        )

    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            return asyncio.run(coro)
        else:
            # Already in an event loop, use run_until_complete
            return loop.run_until_complete(coro)

    def get_token(self) -> str:
        """Get or refresh access token.

        Returns:
            Bearer token string
        """
        return self._run_async(self._async_client.get_token())

    def get_cabinets(
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
        return self._run_async(self._async_client.get_cabinets(page, page_size))

    def get_components(self, cabinet_sn: str) -> list[Component]:
        """Fetch components for a specific cabinet.

        Args:
            cabinet_sn: Cabinet serial number

        Returns:
            List of Component objects
        """
        return self._run_async(self._async_client.get_components(cabinet_sn))

    def get_projects(self) -> list[Project]:
        """Fetch all projects, the top level of the hierarchy (v2.2.0+).

        Returns:
            List of Project objects
        """
        return self._run_async(self._async_client.get_projects())

    def get_project_sites(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 100,
    ) -> list[Site]:
        """Fetch the sites (power stations) of a project with pagination (v2.2.0+).

        Args:
            project_id: Project UUID (from get_projects())
            page: Page number (1-indexed)
            page_size: Number of records per page (API max 1000)

        Returns:
            List of Site objects for the requested page
        """
        return self._run_async(self._async_client.get_project_sites(project_id, page, page_size))

    def get_site_devices(self, site_id: str) -> list[Device]:
        """Fetch the devices of a site, the leaf level of the hierarchy (v2.2.0+).

        Args:
            site_id: Site UUID (from get_project_sites())

        Returns:
            List of Device objects
        """
        return self._run_async(self._async_client.get_site_devices(site_id))

    def subscribe_mqtt_topics(self, mqtt_client_id: str, sn: str, mode: int = 1) -> dict[str, Any]:
        """Subscribe to MQTT topics for a device or component.

        Args:
            mqtt_client_id: MQTT Client ID (obtained from /comm/client endpoint)
            sn: Device or component serial number
            mode: Topic mode - 1 for device/cabinet level, 2 for component level (default: 1)

        Returns:
            Subscription result dictionary containing list of MQTT topics
        """
        return self._run_async(self._async_client.subscribe_mqtt_topics(mqtt_client_id, sn, mode))

    def get_mqtt_credentials(self) -> dict[str, Any]:
        """Get MQTT broker credentials from /comm/client endpoint.

        Returns:
            Dictionary with keys:
                - id: MQTT Client ID (use for subscribe_mqtt_topics())
                - username: MQTT broker username
                - password: MQTT broker password
                - token: API access token
        """
        return self._run_async(self._async_client.get_mqtt_credentials())

    def close(self) -> None:
        """Close HTTP client."""
        self._run_async(self._async_client.close())

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
