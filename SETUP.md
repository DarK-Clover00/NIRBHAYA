# NIRBHAYA Setup Guide

This guide will help you set up the NIRBHAYA Women's Safety Application development environment.

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Manual Setup

### 1. Prerequisites

Install the following software:

- Python 3.9 or higher
- PostgreSQL 13+ with PostGIS extension
- Redis 6+
- Git

### 2. Install PostgreSQL with PostGIS

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis
```

#### macOS
```bash
brew install postgresql postgis
```

#### Windows
Download and install from:
- PostgreSQL: https://www.postgresql.org/download/windows/
- PostGIS: https://postgis.net/windows_downloads/

### 3. Install Redis

#### Ubuntu/Debian
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Download from: https://github.com/microsoftarchive/redis/releases

### 4. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE nirbhaya_db;
CREATE USER nirbhaya_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nirbhaya_db TO nirbhaya_user;

# Connect to the database
\c nirbhaya_db

# Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION "uuid-ossp";

# Verify PostGIS installation
SELECT PostGIS_Version();

# Exit
\q
```

### 5. Clone Repository

```bash
git clone <repository-url>
cd WOMEN_SAFETY
```

### 6. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 7. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 8. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

Required configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Generate a secure random key
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key
- `GOOGLE_PLACES_API_KEY`: Your Google Places API key
- `GOOGLE_STREET_VIEW_API_KEY`: Your Street View API key
- `GOVERNMENT_API_URL`: Government system API endpoint
- `GOVERNMENT_API_KEY`: Government API key
- `GOVERNMENT_API_SECRET`: Government API secret

### 9. Set Up Database Schema

```bash
# Enable PostGIS extension (if not done manually)
python scripts/setup_db.py

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 10. Verify Installation

```bash
# Test database connection
python -c "from backend.database import engine; print('Database connected:', engine.connect())"

# Test Redis connection
python -c "from backend.redis_client import redis_client; print('Redis connected:', redis_client.ping())"
```

## Running the Application

### Backend API

```bash
# Option 1: Using Python directly
python backend/main.py

# Option 2: Using uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using the script
bash scripts/run_backend.sh
```

The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Mobile Client

```bash
# Option 1: Using Python directly
python mobile/main.py

# Option 2: Using the script
bash scripts/run_mobile.sh
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m property      # Property-based tests only
pytest -m integration   # Integration tests only

# Run tests for specific module
pytest tests/test_auth.py
pytest tests/test_models.py
```

View coverage report:
```bash
# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Development Workflow

### Creating Database Migrations

When you modify database models:

```bash
# Generate migration automatically
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Apply the migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Code Quality

```bash
# Format code with black
black backend/ mobile/ tests/

# Check code style with flake8
flake8 backend/ mobile/ tests/

# Type checking with mypy (optional)
mypy backend/
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log  # Linux
tail -f /usr/local/var/log/postgres.log  # macOS
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log  # Linux
tail -f /usr/local/var/log/redis.log  # macOS
```

### PostGIS Extension Issues

```bash
# Verify PostGIS is installed
sudo -u postgres psql -c "SELECT PostGIS_Version();"

# If not installed, install PostGIS package
sudo apt-get install postgresql-*-postgis-*  # Ubuntu
brew install postgis  # macOS
```

### Python Dependencies Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# If specific package fails, install system dependencies
# For psycopg2:
sudo apt-get install libpq-dev python3-dev  # Ubuntu

# For opencv-python:
sudo apt-get install python3-opencv  # Ubuntu
```

### Migration Issues

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Downgrade to specific revision
alembic downgrade <revision_id>

# Stamp database to specific revision (without running migrations)
alembic stamp <revision_id>
```

## Next Steps

After successful setup:

1. Review the [README.md](README.md) for project overview
2. Check the API documentation at http://localhost:8000/docs
3. Review the [design document](.kiro/specs/nirbhaya-safety-app/design.md)
4. Start implementing features according to the [task list](.kiro/specs/nirbhaya-safety-app/tasks.md)

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs
3. Check database and Redis connectivity
4. Verify all environment variables are set correctly
5. Ensure all prerequisites are installed

## Production Deployment

For production deployment, additional steps are required:

1. Use production-grade database (managed PostgreSQL with PostGIS)
2. Use production-grade Redis (managed Redis or Redis Cluster)
3. Set up SSL/TLS certificates
4. Configure proper CORS origins
5. Set up monitoring and logging
6. Configure backup and disaster recovery
7. Set up CI/CD pipeline
8. Implement rate limiting and DDoS protection
9. Use environment-specific configuration
10. Set DEBUG=False in production

Refer to deployment documentation for detailed instructions.
