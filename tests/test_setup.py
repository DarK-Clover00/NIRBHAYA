"""
Basic setup verification tests
"""
import pytest


def test_imports():
    """Test that all core modules can be imported"""
    try:
        from backend import config
        from backend import database
        from backend import redis_client
        from backend import auth
        from backend.models import User, EmergencyContact, IncidentReport
        from backend.models import SOSEvent, RouteRiskCache, TrustScoreEvent
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_config_loaded():
    """Test that configuration is loaded"""
    from backend.config import settings
    
    assert settings is not None
    assert hasattr(settings, 'DATABASE_URL')
    assert hasattr(settings, 'REDIS_URL')
    assert hasattr(settings, 'JWT_SECRET_KEY')


def test_database_models():
    """Test that database models are properly defined"""
    from backend.models import User, EmergencyContact
    
    # Check User model has required fields
    assert hasattr(User, 'id')
    assert hasattr(User, 'phone_number')
    assert hasattr(User, 'trust_score')
    assert hasattr(User, 'device_fingerprint')
    
    # Check EmergencyContact model has required fields
    assert hasattr(EmergencyContact, 'id')
    assert hasattr(EmergencyContact, 'user_id')
    assert hasattr(EmergencyContact, 'phone_number')


def test_auth_functions():
    """Test that auth functions are available"""
    from backend.auth import (
        generate_device_fingerprint,
        create_access_token,
        decode_access_token
    )
    
    # Test device fingerprint generation
    fingerprint = generate_device_fingerprint()
    assert fingerprint is not None
    assert len(fingerprint) > 0
    
    # Test token creation
    token = create_access_token({"sub": "test-user"})
    assert token is not None
    assert len(token) > 0
