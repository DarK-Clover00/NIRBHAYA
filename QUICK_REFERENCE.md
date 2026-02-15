# NIRBHAYA Quick Reference Guide

## 🎨 Indian Tricolour Theme

### Color Codes (Copy-Paste Ready)
```python
SAFFRON = "#FF9933"      # Emergency, SOS, High Risk
INDIA_GREEN = "#138808"  # Safe, Success, Trust
NAVY_BLUE = "#000080"    # Text, Icons, Borders
WHITE = "#FFFFFF"        # Backgrounds
```

---

## 🧮 Safety Score Formula

### New Optimized Weights
```python
safety_score = (
    crowd_density_score * 0.35 +    # Increased from 0.30
    crime_history_score * 0.30 +    # Maintained
    commercial_activity_score * 0.25 + # Increased from 0.20
    lighting_score * 0.10           # Maintained
)
```

### Classification
- **SAFE**: score > 70 (Green card)
- **MEDIUM**: 40 ≤ score ≤ 70 (Yellow/White card)
- **HIGH RISK**: score < 40 (Saffron card)

---

## 🚀 Running the App

### Start Services
```bash
# 1. Start databases
docker compose up -d

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Run backend
python run.py

# 4. View API docs
# Open: http://localhost:8000/docs
```

### Run Mobile App
```bash
# In a new terminal
venv\Scripts\activate
python mobile/main.py
```

---

## 📊 Redis Commands (Location Tracking)

### Store Location Ping
```python
redis_client.geoadd(
    "location_pings",
    longitude,
    latitude,
    device_id
)
redis_client.expire(f"location_pings:{device_id}", 60)  # 60s TTL
```

### Query Nearby Devices
```python
nearby = redis_client.georadius(
    "location_pings",
    longitude,
    latitude,
    50,  # 50 meters radius
    unit='m',
    withdist=True
)
```

---

## 🎯 Key Features

### 1. Crowd Mesh (Heartbeat System)
- Every device sends location every 30 seconds
- Stored in Redis with 60-second TTL
- Automatic cleanup (no historical data)
- Privacy: Aggregated into 100m zones

### 2. Route Safety Analysis
- Divide route into 100m segments
- Query crowd density (Redis GEORADIUS)
- Query crime data (PostgreSQL + PostGIS)
- Query open shops (Google Places API)
- Calculate weighted score
- Suggest safer alternatives if HIGH RISK

### 3. SOS Radar
- Swipe Saffron slider to activate
- Creates 50m geofence in Redis
- Finds nearby devices (GEORADIUS)
- Sends push notifications to nearby users
- Displays circular radar UI
- Tap device to report as suspect

### 4. Trust Score
- Starts at 50 (Neutral)
- Reported during SOS: -10
- Assisted during SOS: +5
- False alarm: -15
- Classification: Fraud (0), Suspected (1-30), Normal (31-100)

---

## 📱 UI Screens

### 1. SafeMap (Home)
- Saffron app bar
- Google Maps with crowd heatmap
- Search bar (Navy Blue border)
- Floating SOS button (Saffron)

### 2. Route Selection
- Map with 2 route polylines (Green = safe, Saffron = risky)
- Bottom sheet with route cards
- Green card: "SAFEST ROUTE" with SELECT button
- Saffron card: "FASTEST ROUTE" with NOT RECOMMENDED button

### 3. SOS Radar
- Pulsing Saffron header
- Circular radar with tricolour gradient
- Distance rings (10m, 25m, 50m)
- Device dots (tap to report)
- "Record Evidence" button (Green)
- "Swipe to Deactivate" slider

### 4. Profile
- Trust score with Green progress bar
- Statistics cards (Navy Blue)
- Emergency contacts list
- "Add Contact" button (Green)

---

## 🗄️ Database Quick Reference

### PostgreSQL Tables
- `users` - User accounts, trust scores, device fingerprints
- `emergency_contacts` - Max 5 per user
- `incident_reports` - Reports with geolocation and evidence
- `sos_events` - SOS activations with geofence data
- `route_risk_cache` - Cached route analysis (1 hour TTL)
- `trust_score_events` - Audit trail for trust score changes

### Redis Keys
- `location_pings` - Geospatial set (60s TTL)
- `sos_geofences` - Active SOS geofences
- `crowd_zones:{zone_id}` - Aggregated crowd data (120s TTL)
- `route:{route_hash}` - Cached route scores (1 hour TTL)

---

## 🧪 Testing

### Run Tests
```bash
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest -m property       # Property-based tests
pytest --cov=backend     # With coverage
```

### Test Specific Module
```bash
pytest tests/test_telemetry.py -v
pytest tests/test_auth.py -v
```

---

## 📚 Documentation Files

### Specs
- `.kiro/specs/nirbhaya-safety-app/requirements.md` - All requirements
- `.kiro/specs/nirbhaya-safety-app/design.md` - Architecture & algorithms
- `.kiro/specs/nirbhaya-safety-app/ui-design.md` - UI specifications with code
- `.kiro/specs/nirbhaya-safety-app/tasks.md` - Implementation tasks

### Setup Guides
- `README.md` - Project overview
- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - Quick start guide
- `RUNNING_ISSUES.md` - Troubleshooting
- `ARCHITECTURE_UPDATES.md` - Recent changes

---

## 🔧 Common Commands

### Database Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Docker
```bash
docker compose up -d      # Start services
docker compose down       # Stop services
docker compose ps         # Check status
docker compose logs       # View logs
```

### Python Environment
```bash
python -m venv venv       # Create virtual environment
venv\Scripts\activate     # Activate (Windows)
pip install -r requirements.txt  # Install dependencies
```

---

## 🎯 Current Status

### ✅ Completed
- Task 1: Project structure, database models, authentication
- Task 2.1: Telemetry service (location ping ingestion)

### 🔄 Next Tasks
- Task 2.2-2.6: Crowd density aggregation
- Task 4: Route analyzer with new weights
- Task 15: Flet UI with tricolour theme

---

## 💡 Quick Tips

1. **Always use tricolour colors** - No other colors in the UI
2. **Test with Redis** - Location data must go to Redis, not PostgreSQL
3. **Cache route scores** - 1 hour TTL to reduce API calls
4. **Privacy first** - Aggregate locations, anonymize device IDs
5. **Performance matters** - Target <3s for route analysis, <2s for SOS

---

## 🆘 Need Help?

### Check These First
1. Is Docker running? `docker compose ps`
2. Is virtual environment activated? Look for `(venv)` in terminal
3. Are dependencies installed? `pip list`
4. Is backend running? Visit `http://localhost:8000/health`

### Common Issues
- **Import errors**: Use `python run.py` not `python backend/main.py`
- **Database errors**: Check Docker containers are running
- **Redis errors**: Verify Redis container is healthy

---

**Last Updated:** February 13, 2026
**Version:** 2.0 (Tricolour Theme)
