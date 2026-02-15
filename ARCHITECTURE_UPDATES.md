# NIRBHAYA Architecture Updates

## Summary of Changes

This document outlines the architectural and design updates made to the NIRBHAYA Women's Safety Application based on the optimized specifications.

---

## 1. Visual Identity: Indian Tricolour Theme

### New Design Language

The entire application now follows a **strict Indian Tricolour theme**:

**Color Palette:**
- **Saffron (#FF9933)**: Emergency actions, SOS button, high-risk warnings, app headers
- **India Green (#138808)**: Safe routes, success states, trust score indicators
- **White (#FFFFFF)**: Primary backgrounds, content areas
- **Navy Blue (#000080)**: Text, icons, borders (Ashoka Chakra color)

**Why This Matters:**
- Creates a patriotic, trustworthy brand identity
- Instantly recognizable as an Indian safety initiative
- Color psychology: Saffron = urgency/action, Green = safety/peace, Navy Blue = trust/authority

---

## 2. Safety Score Algorithm Optimization

### Updated Weights

**Previous:**
```
Safety_Score = (Crime × 0.40) + (Crowd × 0.30) + (Commercial × 0.20) + (Lighting × 0.10)
```

**New (Optimized for Indian Context):**
```
Safety_Score = (Crowd × 0.35) + (Crime × 0.30) + (Commercial × 0.25) + (Lighting × 0.10)
```

**Rationale:**
1. **Crowd Density (35%)** - Increased from 30%
   - "Safety in numbers" is critical in Indian urban contexts
   - Real-time data from Redis GEORADIUS provides accurate crowd sensing
   - More weight on live data vs historical data

2. **Crime History (30%)** - Maintained
   - Still crucial for risk assessment
   - Uses government crime database integration

3. **Commercial Activity (25%)** - Increased from 20%
   - "Eyes on the street" principle is vital in India
   - Open shops = witnesses = deterrent to crime
   - Google Places API provides real-time open/closed status

4. **Lighting (10%)** - Kept minimal
   - Street lighting data can be unreliable
   - Installed lights may not be functional
   - Treated as supplementary indicator only

### Technical Improvements

**Crowd Detection Radius:**
- **Changed from 100m to 50m** for more precise crowd density measurement
- Tighter radius = more accurate "safety in numbers" assessment
- Reduces false positives from distant crowds

---

## 3. Architecture Enhancements

### Redis as Primary Real-Time Engine

**Why Redis for Location Data:**
```
❌ PostgreSQL: Cannot handle millions of location updates per second
✅ Redis: In-memory, sub-100ms queries, automatic TTL expiry
```

**Implementation:**
- Every device sends heartbeat `{user_id, lat, long}` every 30 seconds
- Stored in Redis with `GEOADD` command
- 60-second TTL (Time-To-Live) - automatic cleanup
- `GEORADIUS` queries for instant crowd density checks

**Performance:**
- Location ping processing: <50ms
- Crowd density query: <100ms
- Supports 10,000+ concurrent pings/second

### WebSocket for Real-Time SOS

**SOS Radar Implementation:**
1. User activates SOS → WebSocket connection opens
2. Backend performs `GEORADIUS` query (50m radius)
3. Nearby device IDs sent to victim's radar UI
4. Push notifications sent to nearby devices
5. Real-time updates every 5 seconds

---

## 4. UI/UX Specifications

### New UI Design Document

Created comprehensive UI specification (`.kiro/specs/nirbhaya-safety-app/ui-design.md`) with:

**Screen Designs:**
1. **SafeMap Screen** - Saffron app bar, map with tricolour markers
2. **Route Selection** - Green card for safe route, Saffron card for risky route
3. **SOS Radar** - Circular radar with tricolour gradient, pulsing Saffron header
4. **Profile Screen** - Trust score with Green progress bar, Navy Blue statistics cards

**Component Library:**
- Buttons (Primary/Saffron, Success/Green, Secondary/Navy Blue)
- Cards (Standard/White, Warning/Saffron, Success/Green)
- Progress bars (Green for safe, Saffron for risk)
- Animations (SOS pulse, radar sweep, card slide-in)

**Flet Code Examples:**
- Complete code snippets for each screen
- Reusable component functions
- Color constants and styling

---

## 5. Technology Stack Confirmation

### Python-Centric Stack

**Frontend:**
- **Flet** (Python-based Flutter wrapper)
- Allows building mobile apps entirely in Python
- Real-time updates via WebSocket
- Google Maps integration

**Backend:**
- **FastAPI** (Fastest Python web framework)
- Async/await for concurrent requests
- Sub-second route analysis
- WebSocket support for SOS

**Databases:**
- **Redis** - Real-time location data, geospatial queries
- **PostgreSQL + PostGIS** - User profiles, crime data, incident reports

**External APIs:**
- Google Maps Directions API (route retrieval)
- Google Places API (commercial activity)
- Google Street View Static API (lighting analysis)
- Government Crime Database API (crime history)

---

## 6. Key Features Implementation

### A. The "Crowd Mesh" (Passive Sensing)

**How It Works:**
```python
# Every 30 seconds, each device sends:
{
  "user_id": "uuid",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timestamp": "2024-02-13T10:30:00Z"
}

# Backend stores in Redis:
redis_client.geoadd("location_pings", longitude, latitude, user_id)
redis_client.expire(f"location_pings:{user_id}", 60)  # 60s TTL
```

**Privacy:**
- No historical location data stored
- Aggregated into 100m zones (minimum 5 devices per zone)
- Anonymized device IDs
- Automatic expiry after 60 seconds

### B. Intelligent Route Scoring

**Process:**
1. User enters destination
2. Google Directions API returns route polyline
3. Divide polyline into 100m segments
4. For each segment:
   - Query Redis for nearby devices (crowd density)
   - Query PostgreSQL for crime hotspots (within 1km)
   - Query Google Places for open shops (within 200m)
   - Analyze Street View images for lighting (optional)
5. Calculate weighted safety score (0-100)
6. Classify: SAFE (>70), MEDIUM (40-70), HIGH RISK (<40)
7. If HIGH RISK, suggest alternative safer route

**UI Display:**
- Green card with ✓ icon for safe route
- Saffron card with ⚠ icon for risky route
- Detailed breakdown of factors
- "SELECT" button (Green) vs "NOT RECOMMENDED" (Gray)

### C. SOS Radar & Suspect Identification

**Activation Flow:**
1. User swipes Saffron "SOS" slider
2. Backend creates geofence (50m radius) in Redis
3. `GEORADIUS` query finds all devices within 50m
4. Push notification sent to nearby devices:
   ```
   "ALERT: Distress signal active in your vicinity.
   Your location and identity are being logged."
   ```
5. Victim's screen shows circular radar with device dots
6. Victim can tap any dot to report as suspect
7. Optional: Start live video recording as evidence

**Radar UI:**
- Circular display with tricolour gradient
- Distance rings (10m, 25m, 50m)
- Victim at center
- Nearby devices as dots (relative position)
- Tap to report functionality
- "Record Evidence" button (Green)
- "Swipe to Deactivate" slider (Navy Blue)

### D. Trust Score System

**Scoring Logic:**
```python
# Starting score: 50 (Neutral)
# Adjustments:
- Reported during SOS: -10 points
- Assisted during SOS: +5 points
- False alarm: -15 points
- Verified help: +10 points
- Multiple reports (3+ in 30 days): -20 points
- Clean record (90 days): +5 points

# Classification:
- 0: Fraud (account flagged)
- 1-30: Suspected
- 31-100: Normal
```

**UI Display:**
- Green progress bar for trust score
- Badge: Bronze (30-50), Silver (51-75), Gold (76-100)
- Statistics: SOS count, assists, reports against

---

## 7. Database Schema

### PostgreSQL Tables

**users:**
```sql
- id (UUID)
- phone_number (unique)
- trust_score (0-100, default 50)
- classification (Normal/Suspected/Fraud)
- device_fingerprint (unique)
- status (active/flagged/banned)
```

**incident_reports:**
```sql
- id (UUID)
- reporter_id (FK to users)
- suspect_device_id (nullable)
- incident_type (SOS_Trigger/Harassment/Poor_Lighting)
- location (PostGIS Point)
- evidence_urls (array)
- government_system_ref
```

**sos_events:**
```sql
- id (UUID)
- user_id (FK to users)
- activation_location (PostGIS Point)
- geofence_radius (default 50m)
- video_stream_url
- nearby_devices_snapshot (JSONB)
```

**crime_hotspots:**
```sql
- id (UUID)
- location (PostGIS Point)
- severity_level (0-100)
- incident_type
- reported_date
```

### Redis Data Structures

**Location Pings:**
```
Key: "location_pings"
Type: Geospatial Set (GEOADD)
Members: device_id
TTL: 60 seconds per member
```

**SOS Geofences:**
```
Key: "sos_geofences"
Type: Geospatial Set
Members: sos_id
TTL: Manual removal on deactivation
```

**Crowd Zones:**
```
Key: "crowd_zones:{zone_id}"
Type: Hash
Fields: device_count, last_updated, zone_bounds
TTL: 120 seconds
```

---

## 8. Performance Targets

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Location ping processing | <50ms | Redis GEOADD |
| Crowd density query | <100ms | Redis GEORADIUS |
| Route safety calculation | <3s | Parallel API calls + caching |
| SOS activation | <2s | WebSocket + Redis |
| Concurrent pings | 10,000/s | Redis connection pooling |

---

## 9. Security & Privacy

**Privacy Measures:**
- Zone-based aggregation (100m radius, min 5 devices)
- Anonymized device IDs (HMAC with daily rotation)
- No historical location storage (60s TTL)
- PII stored separately from device fingerprints

**Security Features:**
- JWT authentication with device fingerprinting
- Rate limiting (100 requests/minute per device)
- Fraud account access restriction
- SQL injection protection (SQLAlchemy ORM)
- HTTPS/TLS for all communications

---

## 10. Implementation Status

### ✅ Completed (Task 1)
- Project structure
- Database models (all 6 tables)
- Redis client with geospatial support
- JWT authentication with device fingerprinting
- Database migrations (Alembic)
- Docker Compose setup

### ✅ Completed (Task 2.1)
- Telemetry service (location ping ingestion)
- Rate limiting
- Redis GEOADD integration
- 60-second TTL on location pings

### 🔄 In Progress
- Task 2.2-2.6: Crowd density aggregation
- Task 4: Route safety analysis
- Task 6: SOS emergency system

### 📋 Pending
- Mobile UI implementation (Flet)
- Google Maps integration
- Video streaming service
- Government API integration

---

## 11. Next Steps

### Immediate (Week 1-2)
1. Complete crowd density aggregation service
2. Implement route analyzer with new weights
3. Create basic Flet UI with tricolour theme

### Short-term (Week 3-4)
1. Implement SOS radar with WebSocket
2. Integrate Google Maps APIs
3. Build trust score management system

### Medium-term (Month 2)
1. Video streaming for evidence
2. Government system integration
3. Comprehensive testing (unit, property, integration)

### Long-term (Month 3+)
1. Performance optimization
2. Security hardening
3. Production deployment
4. User acceptance testing

---

## 12. Files Updated/Created

### Updated Files:
- `.kiro/specs/nirbhaya-safety-app/design.md` - Added tricolour theme, updated algorithm weights
- `.kiro/specs/nirbhaya-safety-app/requirements.md` - (No changes needed, already comprehensive)
- `.kiro/specs/nirbhaya-safety-app/tasks.md` - (No changes needed, tasks remain valid)

### New Files:
- `.kiro/specs/nirbhaya-safety-app/ui-design.md` - Complete UI specification with Flet code examples
- `ARCHITECTURE_UPDATES.md` - This document

---

## 13. Developer Handoff

### To Continue Development:

**1. Review Updated Specs:**
```bash
# Read the updated design document
cat .kiro/specs/nirbhaya-safety-app/design.md

# Review UI specifications
cat .kiro/specs/nirbhaya-safety-app/ui-design.md

# Check task list
cat .kiro/specs/nirbhaya-safety-app/tasks.md
```

**2. Start Next Task:**
```bash
# Task 2.2: Implement crowd density aggregation
# Task 4: Implement route analyzer with new weights (35% crowd, 30% crime, 25% commercial, 10% lighting)
# Task 15: Build Flet UI with Indian Tricolour theme
```

**3. Use Color Constants:**
```python
# In your Flet code, always use:
SAFFRON = "#FF9933"
INDIA_GREEN = "#138808"
NAVY_BLUE = "#000080"
WHITE = "#FFFFFF"
```

**4. Test Safety Score Calculation:**
```python
# Verify new weights:
safety_score = (crowd_score * 0.35) + (crime_score * 0.30) + (commercial_score * 0.25) + (lighting_score * 0.10)
```

---

## Conclusion

The NIRBHAYA application now has:
- ✅ A cohesive Indian Tricolour visual identity
- ✅ Optimized safety scoring algorithm for Indian context
- ✅ Comprehensive UI specifications with Flet code examples
- ✅ Clear architecture for real-time crowd sensing
- ✅ Detailed implementation roadmap

The foundation is solid, and the next phase is to implement the remaining features following the updated specifications.

---

**Last Updated:** February 13, 2026
**Version:** 2.0 (Tricolour Theme + Optimized Algorithm)
