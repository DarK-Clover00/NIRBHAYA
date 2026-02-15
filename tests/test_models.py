"""
Unit tests for database models
"""
import pytest
from backend.models.user import User
from backend.models.emergency_contact import EmergencyContact
from backend.models.trust_score_event import TrustScoreEvent
from sqlalchemy.exc import IntegrityError
from geoalchemy2.elements import WKTElement


def test_create_user(db_session, sample_user_data):
    """Test user creation"""
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.phone_number == sample_user_data["phone_number"]
    assert user.trust_score == 50
    assert user.classification == "Normal"
    assert user.status == "active"
    assert user.created_at is not None


def test_user_trust_score_constraint(db_session, sample_user_data):
    """Test trust score must be between 0 and 100"""
    # Test invalid trust score > 100
    sample_user_data["trust_score"] = 150
    user = User(**sample_user_data)
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()
    
    # Test invalid trust score < 0
    sample_user_data["trust_score"] = -10
    sample_user_data["phone_number"] = "+9999999999"
    user = User(**sample_user_data)
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_unique_phone_number(db_session, sample_user_data):
    """Test phone number must be unique"""
    user1 = User(**sample_user_data)
    db_session.add(user1)
    db_session.commit()
    
    # Try to create another user with same phone number
    sample_user_data["device_fingerprint"] = "different-fingerprint"
    user2 = User(**sample_user_data)
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_unique_device_fingerprint(db_session, sample_user_data):
    """Test device fingerprint must be unique"""
    user1 = User(**sample_user_data)
    db_session.add(user1)
    db_session.commit()
    
    # Try to create another user with same device fingerprint
    sample_user_data["phone_number"] = "+9999999999"
    user2 = User(**sample_user_data)
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_emergency_contact(db_session, sample_user_data):
    """Test emergency contact creation"""
    # Create user first
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    # Create emergency contact
    contact = EmergencyContact(
        user_id=user.id,
        name="John Doe",
        phone_number="+1987654321",
        priority=1
    )
    db_session.add(contact)
    db_session.commit()
    
    assert contact.id is not None
    assert contact.user_id == user.id
    assert contact.name == "John Doe"
    assert contact.phone_number == "+1987654321"
    assert contact.priority == 1


def test_emergency_contact_cascade_delete(db_session, sample_user_data):
    """Test emergency contacts are deleted when user is deleted"""
    # Create user
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    # Create emergency contact
    contact = EmergencyContact(
        user_id=user.id,
        name="John Doe",
        phone_number="+1987654321"
    )
    db_session.add(contact)
    db_session.commit()
    
    contact_id = contact.id
    
    # Delete user
    db_session.delete(user)
    db_session.commit()
    
    # Verify contact is also deleted
    deleted_contact = db_session.query(EmergencyContact).filter_by(id=contact_id).first()
    assert deleted_contact is None


def test_create_trust_score_event(db_session, sample_user_data):
    """Test trust score event creation"""
    # Create user
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    # Create trust score event
    event = TrustScoreEvent(
        user_id=user.id,
        event_type="reported_during_sos",
        score_change=-10,
        previous_score=50,
        new_score=40
    )
    db_session.add(event)
    db_session.commit()
    
    assert event.id is not None
    assert event.user_id == user.id
    assert event.event_type == "reported_during_sos"
    assert event.score_change == -10
    assert event.previous_score == 50
    assert event.new_score == 40
    assert event.created_at is not None


def test_user_classification_constraint(db_session, sample_user_data):
    """Test user classification must be valid"""
    sample_user_data["classification"] = "InvalidClassification"
    user = User(**sample_user_data)
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_status_constraint(db_session, sample_user_data):
    """Test user status must be valid"""
    sample_user_data["status"] = "InvalidStatus"
    user = User(**sample_user_data)
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
