"""HMAC-SHA256 authentication for Elecnova API."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime


def generate_nonce(length: int = 32) -> str:
    """Generate a random nonce for request signing.

    Args:
        length: Length of the nonce string (default: 32)

    Returns:
        Random hexadecimal string
    """
    return secrets.token_hex(length // 2)


def generate_timestamp() -> str:
    """Generate current UTC timestamp in milliseconds.

    Returns:
        String timestamp in milliseconds since epoch
    """
    return str(int(datetime.now(UTC).timestamp() * 1000))


def generate_signature(
    client_id: str,
    client_secret: str,
    timestamp: str,
    nonce: str,
) -> str:
    """Generate HMAC-SHA256 signature for Elecnova API authentication.

    Based on Elecnova API documentation Chapter 3:
    1. Concatenate: clientId + timestamp + nonce
    2. Use clientSecret as HMAC key
    3. Generate SHA-256 hash
    4. Convert to lowercase hex string

    Args:
        client_id: Client ID from Elecnova
        client_secret: Client secret from Elecnova
        timestamp: Current timestamp in milliseconds
        nonce: Random nonce string

    Returns:
        HMAC-SHA256 signature as lowercase hex string
    """
    # Concatenate: clientId + timestamp + nonce
    message = f"{client_id}{timestamp}{nonce}"

    # Generate HMAC-SHA256
    signature = hmac.new(
        key=client_secret.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Return lowercase hex string
    return signature.lower()


def generate_comm_client_signature(
    path: str,
    client_secret: str,
    timestamp: str,
) -> str:
    """Generate signature for /comm/client endpoint.

    Based on Elecnova API v1.3.1 documentation:
    1. Concatenate: PATH + timestamp
    2. Use clientSecret as HMAC key
    3. Generate SHA-256 hash
    4. Convert to hex string
    5. Base64 encode the hex string

    Args:
        path: API path (e.g., "/comm/client")
        client_secret: Client secret from Elecnova
        timestamp: Current timestamp in milliseconds

    Returns:
        Base64-encoded HMAC-SHA256 signature
    """
    import base64

    # Concatenate: PATH + timestamp
    message = f"{path}{timestamp}"

    # Generate HMAC-SHA256 and convert to hex
    hex_signature = hmac.new(
        key=client_secret.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Base64 encode the hex string
    return base64.b64encode(hex_signature.encode("utf-8")).decode("utf-8")


def generate_auth_headers(client_id: str, client_secret: str) -> dict[str, str]:
    """Generate complete authentication headers for API request.

    Args:
        client_id: Client ID from Elecnova
        client_secret: Client secret from Elecnova

    Returns:
        Dictionary of authentication headers
    """
    timestamp = generate_timestamp()
    nonce = generate_nonce()
    signature = generate_signature(client_id, client_secret, timestamp, nonce)

    return {
        "clientId": client_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "sign": signature,
    }
