"""Tests for authentication module."""

import re

from elecnova_client.auth import (
    generate_auth_headers,
    generate_nonce,
    generate_signature,
    generate_timestamp,
)


def test_generate_nonce():
    """Test nonce generation."""
    nonce = generate_nonce(32)
    assert len(nonce) == 32
    assert re.match(r"^[0-9a-f]+$", nonce)

    # Test different lengths
    nonce_16 = generate_nonce(16)
    assert len(nonce_16) == 16

    # Test uniqueness
    nonce1 = generate_nonce(32)
    nonce2 = generate_nonce(32)
    assert nonce1 != nonce2


def test_generate_timestamp():
    """Test timestamp generation."""
    timestamp = generate_timestamp()
    assert timestamp.isdigit()
    assert len(timestamp) == 13  # Milliseconds since epoch


def test_generate_signature():
    """Test HMAC-SHA256 signature generation."""
    client_id = "test_client"
    client_secret = "test_secret"
    timestamp = "1234567890000"
    nonce = "abcdef1234567890"

    signature = generate_signature(client_id, client_secret, timestamp, nonce)

    # Should be lowercase hex string
    assert re.match(r"^[0-9a-f]+$", signature)
    assert len(signature) == 64  # SHA-256 produces 32 bytes = 64 hex chars

    # Should be deterministic
    signature2 = generate_signature(client_id, client_secret, timestamp, nonce)
    assert signature == signature2

    # Should change with different inputs
    signature3 = generate_signature(client_id, client_secret, timestamp, "different_nonce")
    assert signature != signature3


def test_generate_auth_headers():
    """Test complete auth headers generation."""
    client_id = "test_client"
    client_secret = "test_secret"

    headers = generate_auth_headers(client_id, client_secret)

    assert "clientId" in headers
    assert "timestamp" in headers
    assert "nonce" in headers
    assert "sign" in headers

    assert headers["clientId"] == client_id
    assert headers["timestamp"].isdigit()
    assert len(headers["nonce"]) == 32
    assert re.match(r"^[0-9a-f]{64}$", headers["sign"])
