#!/bin/bash
# Script to create initial database migration

echo "Creating initial database migration..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create initial migration
alembic revision --autogenerate -m "Initial schema with users, emergency_contacts, incident_reports, sos_events, route_risk_cache, trust_score_events"

echo "Migration created successfully"
echo "Run 'alembic upgrade head' to apply the migration"
