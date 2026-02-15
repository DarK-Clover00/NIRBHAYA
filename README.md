# NIRBHAYA Women's Safety Application

A mobile-first safety application designed to enhance women's safety through intelligent route analysis, real-time crowd density tracking, and emergency response systems.

## Features

- **Route Safety Analysis**: Multi-factor safety scoring based on crime data, crowd density, commercial activity, and lighting
- **Real-Time Crowd Density**: Distributed network of devices providing live crowd density heatmaps
- **SOS Emergency System**: One-tap emergency activation with geofenced device detection
- **Radar Interface**: Visual display of nearby devices during emergencies
- **Trust Score System**: User reliability tracking and fraud detection
- **Incident Reporting**: Report suspicious activity with evidence attachment
- **Privacy-Preserving**: Zone-based aggregation protects individual privacy

## Architecture

- **Backend**: FastAPI (Python)
- **Mobile Client**: Flet (Python)
- **Database**: PostgreSQL with PostGIS extension
- **Cache/Geospatial**: Redis
- **External APIs**: Google Maps, Google Places, Google Street View

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ with PostGIS extension
- Redis 6+
- Google Maps API key
- Government System API credentials (for crime data)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd WOMEN_SAFETY
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL with PostGIS

```bash
# Install PostgreSQL and PostGIS
# On Ubuntu:
sudo apt-get install postgresql postgresql-contrib postgis

# Create database
sudo -u postgres psql
CREATE DATABASE nirbhaya_db;
\c nirbhaya_db
CREATE EXTENSION postgis;
CREATE USER nirbhaya_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nirbhaya_db TO nirbhaya_user;
\q
```

### 5. Set up Redis

```bash
# On Ubuntu:
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### 6. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 7. Run database migrations

```bash
alembic upgrade head
```

## Running the Application

### Quick Start (Easiest Way)

```bash
# Option 1: Use the run script (Windows)
run.bat

# Option 2: Use Python directly
python run.py

# Option 3: Use module syntax
python -m backend.main
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### ⚠️ Important: Database Services Required

Before running, make sure PostgreSQL and Redis are running:

**Using Docker (Recommended):**
```bash
docker compose up -d
```

**Or use cloud services** (see RUNNING_ISSUES.md for details)

### Mobile Client

```bash
python mobile/main.py
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run property-based tests only
pytest -m property

# Run unit tests only
pytest -m unit
```

### Creating Database Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Style

```bash
# Format code
black backend/ mobile/

# Lint code
flake8 backend/ mobile/
```

## Project Structure

```
WOMEN_SAFETY/
├── backend/
│   ├── api/              # API endpoints
│   ├── models/           # Database models
│   ├── services/         # Business logic services
│   ├── auth.py           # Authentication
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   ├── redis_client.py   # Redis client
│   └── main.py           # FastAPI application
├── mobile/
│   ├── views/            # UI screens
│   ├── services/         # Mobile services
│   └── main.py           # Flet application
├── alembic/              # Database migrations
├── tests/                # Test files
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Telemetry
- `POST /api/v1/telemetry/ping` - Submit location ping

### Route Analysis
- `POST /api/v1/routes/analyze` - Analyze route safety

### SOS
- `POST /api/v1/sos/activate` - Activate SOS mode
- `POST /api/v1/sos/deactivate` - Deactivate SOS mode
- `GET /api/v1/sos/radar` - Get nearby devices

### Incident Reporting
- `POST /api/v1/report/suspect` - Report suspicious device

### User Profile
- `GET /api/v1/user/profile` - Get user profile
- `POST /api/v1/user/emergency-contacts` - Manage emergency contacts

## Security

- JWT-based authentication with device fingerprinting
- Rate limiting (100 requests/minute per device)
- Privacy-preserving location aggregation
- PII sanitization in logs
- Fraud detection and account flagging

## Performance

- Location ping processing: <50ms
- Route analysis: <3 seconds
- SOS activation: <2 seconds
- Geospatial queries: <100ms
- Supports 10,000+ concurrent location pings/second

