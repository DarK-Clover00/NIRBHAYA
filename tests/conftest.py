"""
Pytest configuration and fixtures for NIRBHAYA tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.config import settings
import redis


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine
    Uses a separate test database to avoid affecting production data
    """
    # Use test database URL (modify DATABASE_URL to use test database)
    test_db_url = settings.DATABASE_URL.replace("/nirbhaya_db", "/nirbhaya_test_db")
    engine = create_engine(test_db_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Create a new database session for each test
    Rolls back changes after each test
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def redis_client():
    """
    Create a Redis client for testing
    Flushes test database after each test
    """
    # Use Redis database 15 for testing
    test_redis_url = settings.REDIS_URL.replace("/0", "/15")
    client = redis.from_url(test_redis_url, decode_responses=True)
    
    yield client
    
    # Clean up test data
    client.flushdb()
    client.close()


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing
    """
    return {
        "phone_number": "+1234567890",
        "device_fingerprint": "test-device-fingerprint-123",
        "trust_score": 50,
        "classification": "Normal",
        "status": "active"
    }


@pytest.fixture
def sample_location():
    """
    Sample location coordinates for testing
    """
    return {
        "latitude": 37.7749,
        "longitude": -122.4194
    }


@pytest.fixture
def mock_redis():
    """
    Mock Redis client for unit testing
    """
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.geoadd.return_value = 1
    mock.setex.return_value = True
    mock.hset.return_value = True
    mock.expire.return_value = True
    mock.exists.return_value = True
    mock.geopos.return_value = [(-122.4194, 37.7749)]
    mock.hgetall.return_value = {}
    mock.georadius.return_value = []
    mock.zrange.return_value = []
    mock.zrem.return_value = 1
    mock.delete.return_value = 1
    return mock

