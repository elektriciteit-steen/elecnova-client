"""Custom exceptions for Elecnova client."""


class ElecnovaAPIError(Exception):
    """Base exception for Elecnova API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ElecnovaAuthError(ElecnovaAPIError):
    """Authentication failed."""

    pass


class ElecnovaRateLimitError(ElecnovaAPIError):
    """Rate limit exceeded."""

    pass


class ElecnovaTimeoutError(ElecnovaAPIError):
    """Request timeout."""

    pass
