# How to Fix Running Issues

## Problem Identified

The app wasn't running because:
1. ❌ Python couldn't find the `backend` module (import error)
2. ❌ PostgreSQL and Redis are not installed/running

## ✅ SOLUTION: Easy Way to Run the App

### Option 1: Use the New Run Script (Simplest)

```bash
# Just double-click this file or run:
run.bat
```

Or if you prefer Python directly:
```bash
python run.py
```

### Option 2: Use Python Module Syntax

```bash
python -m backend.main
```

## ⚠️ Important: Database Services Required

The app needs PostgreSQL and Redis to work. You have 3 options:

### Option A: Install Docker Desktop (Recommended - Easiest)

1. **Download Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. **Install and start Docker Desktop**
3. **Run this command**:
   ```bash
   docker compose up -d
   ```
   This automatically starts PostgreSQL with PostGIS and Redis!

### Option B: Use Online Database Services (No Installation)

**PostgreSQL with PostGIS:**
- ElephantSQL: https://www.elephantsql.com/ (Free tier available)
- Supabase: https://supabase.com/ (Free tier with PostGIS)
- Neon: https://neon.tech/ (Free tier)

**Redis:**
- Redis Cloud: https://redis.com/try-free/ (Free tier)
- Upstash: https://upstash.com/ (Free tier)

Then update your `.env` file with the connection strings:
```env
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://user:password@host:port
```

### Option C: Install Locally (Advanced)

**Install PostgreSQL:**
1. Download from: https://www.postgresql.org/download/windows/
2. Install with PostGIS extension
3. Create database: `nirbhaya_db`
4. Create user: `nirbhaya_user` with password `nirbhaya_password`

**Install Redis:**
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Install and start the service

## Quick Test Without Database (Development Mode)

If you just want to see if the code runs, you can temporarily comment out database connections:

1. Open `backend/main.py`
2. Comment out any database initialization
3. Run: `python run.py`

## Complete Setup Steps (First Time)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start databases (if using Docker)
docker compose up -d

# 5. Run the app
python run.py
```

## Verify It's Working

Once running, open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the interactive API documentation!

## Common Errors and Fixes

### Error: "ModuleNotFoundError: No module named 'backend'"
**Fix**: Use `python run.py` or `python -m backend.main` instead of `python backend/main.py`

### Error: "No module named 'pydantic_settings'"
**Fix**: Install dependencies: `pip install -r requirements.txt`

### Error: Database connection failed
**Fix**: Make sure PostgreSQL is running or use Docker: `docker compose up -d`

### Error: Redis connection failed
**Fix**: Make sure Redis is running or use Docker: `docker compose up -d`

### Error: "docker-compose not found"
**Fix**: Install Docker Desktop from https://www.docker.com/products/docker-desktop/

## Need Help?

The app is currently set up with:
- ✅ Backend API structure
- ✅ Database models
- ✅ Authentication system
- ⏳ Feature endpoints (being implemented)

You can start the backend even without all features implemented - it will show you the available endpoints in the API docs!
