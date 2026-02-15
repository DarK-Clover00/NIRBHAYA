"""
Unit tests for authentication module
"""
import pytest
from backend.auth import (
    generate_device_fingerprint,
    hash_device_fingerprint,
    create_access_token,
    decode_access_token,
    verify_device_fingerprint
)
from backend.models.user import User
from datetime import timedelta
from fastapi import HTTPException


def test_generate_device_fingerprint():
    """Test device fingerprint generation"""
    fingerprint1 = generate_device_fingerprint()
    fingerprint2 = generate_device_fingerprint()
    
    # Fingerprints should be unique
    assert fingerprint1 != fingerprint2
    assert len(fingerprint1) > 0
    assert len(fingerprint2) > 0


def test_hash_device_fingerprint():
    """Test device fingerprint hashing"""
    fingerprint = "test-fingerprint-123"
    hash1 = hash_device_fingerprint(fingerprint)
    hash2 = hash_device_fingerprint(fingerprint)
    
    # Same input should produce same hash
    assert hash1 == hash2
    
    # Hash should be different from input
    assert hash1 != fingerprint
    
    # Hash should be 64 characters (SHA256)
    assert len(hash1) == 64


def test_create_access_token():
    """Test JWT token creation"""
    data = {
        "sub": "user-id-123",
        "device_fingerprint": "device-fp-123"
    }
    
    token = create_access_token(data)
    
    assert token is not None
    assert len(token) > 0
    assert isinstance(token, str)


def test_create_access_token_with_expiry():
    """Test JWT token creation with custom expiry"""
    data = {
        "sub": "user-id-123",
        "device_fingerprint": "device-fp-123"
    }
    
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    
    assert token is not None
    
    # Decode and verify expiry is set
    payload = decode_access_token(token)
    assert "exp" in payload


def test_decode_access_token():
    """Test JWT token decoding"""
    data = {
        "sub": "user-id-123",
        "device_fingerprint": "device-fp-123"
    }
    
    token = create_access_token(data)
    payload = decode_access_token(token)
    
    assert payload["sub"] == "user-id-123"
    assert payload["device_fingerprint"] == "device-fp-123"
    assert "exp" in payload


def test_decode_invalid_token():
    """Test decoding invalid JWT token"""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(invalid_token)
    
    assert exc_info.value.status_code == 401


def test_verify_device_fingerprint(db_session, sample_user_data):
    """Test device fingerprint verification"""
    # Create user
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    # Verify correct fingerprint
    assert verify_device_fingerprint(user, sample_user_data["device_fingerprint"]) is True
    
    # Verify incorrect fingerprint
    assert verify_device_fingerprint(user, "wrong-fingerprint") is False
