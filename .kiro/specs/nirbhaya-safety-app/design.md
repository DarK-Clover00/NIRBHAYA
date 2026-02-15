# Design Document: NIRBHAYA Women's Safety Application

## Overview

NIRBHAYA is a distributed safety platform that transforms mobile devices into a mesh network for real-time safety monitoring. The architecture follows a client-server model with a Python-based mobile frontend (Flet framework) and a FastAPI backend. The system processes location data from thousands of devices to generate crowd density heatmaps, analyzes routes using multi-factor safety scoring, and provides emergency response capabilities with geofenced device tracking.

The design emphasizes privacy preservation through data aggregation, real-time performance for emergency features, and scalability for nationwide deployment. Key technical components include Redis-based geospatial indexing for sub-100ms location queries, PostgreSQL with PostGIS for persistent storage, and integration with Google Maps APIs for route analysis and visualization.

## Visual Identity: Indian Tricolour Theme

NIRBHAYA's design language strictly follows the **Indian Tricolour theme**, representing national integrity, safety, and pride.

### Color Palette

**Primary Colors:**
- **Saffron (#FF9933)**: Used for headers, high-priority buttons, SOS triggers, and critical alerts
- **India Green (#138808)**: Used for "Safe Route" indicators, trust score bars, success states, and positive confirmations
- **White (#FFFFFF)**: Primary background color for clean, professional appearance
- **Navy Blue (#000080)**: Ashoka Chakra color used for text, icons, borders, and secondary elements

**Color Usage Guidelines:**
- **Saffron**: Emergency actions, warnings, high-risk indicators, SOS button
- **Green**: Safe routes, verified users, successful operations, trust badges
- **Navy Blue**: Text, icons, borders, inactive states
- **White**: Backgrounds, cards, content areas

### Typography
- **Primary Font**: Roboto or Open Sans (clean, sans-serif)
- **Header Weight**: Bold (700)
- **Body Weight**: Regular (400)
- **Small Text**: Light (300)

### UI Components Theme
- **Buttons**: Rounded corners (8px), Saffron for primary actions, Green for confirmations
- **Cards**: White background with Navy Blue borders (1px), subtle shadow
- **Icons**: Navy Blue with Saffron/Green accents for status
- **Progress Bars**: Green fill on White/Navy Blue background
- **Radar Display**: Tricolour gradient (Saffron → White → Green)
- **Map Markers**: Saffron for danger zones, Green for safe zones, Navy Blue for neutral

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile Clients (Flet)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SafeMap UI  │  │  SOS Radar   │  │   Profile    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Telemetry   │  │    Route     │  │     SOS      │      │
│  │   Service    │  │   Analyzer   │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    Redis     │   │  PostgreSQL  │   │ Google Maps  │
│  (Geospatial)│   │  + PostGIS   │   │     API      │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Component Responsibilities

**Mobile Client (Flet)**:
- Renders map interface with crowd density heatmap
- Sends location pings every 30-60 seconds
- Handles SOS activation and radar visualization
- Manages local caching for offline functionality
- Captures and uploads evidence (video/images)

**API Gateway (FastAPI)**:
- Authenticates requests using JWT tokens and device fingerprints
- Routes requests to appropriate service handlers
- Implements rate limiting (100 requests/minute per device)
- Handles WebSocket connections for real-time SOS updates

**Telemetry Service**:
- Receives and validates location pings
- Stores pings in Redis with 60-second TTL
- Aggregates pings into geographic zones (100m radius)
- Generates crowd density heatmap data

**Route Analyzer**:
- Fetches routes from Google Directions API
- Calculates safety scores using weighted algorithm
- Queries crime data from government systems
- Analyzes street lighting using OpenCV on Street View images
- Caches route scores for 1 hour

**SOS Service**:
- Manages SOS activation/deactivation
- Creates and maintains geofences (50m radius)
- Queries nearby devices using Redis GEORADIUS
- Sends alerts to emergency contacts via SMS/push notifications
- Handles video streaming and evidence storage

**Trust Score Manager**:
- Calculates and updates user trust scores
- Applies score adjustments based on events
- Classifies users (Normal/Suspected/Fraud)
- Triggers account reviews for fraud cases

### Data Flow

**Location Ping Flow**:
1. Mobile client sends location ping every 30-60 seconds
2. API Gateway validates device fingerprint and user token
3. Telemetry Service stores ping in Redis with GEOADD command
4. Redis automatically expires ping after 60 seconds
5. Aggregation service groups pings into zones every 10 seconds
6. Heatmap data pushed to connected clients via WebSocket

**Route Analysis Flow**:
1. User selects destination in mobile app
2. Client requests routes from backend
3. Route Analyzer fetches routes from Google Directions API
4. For each route segment:
   - Query crime data within 1km radius
   - Fetch crowd density from Redis
   - Query open businesses from Google Places
   - Analyze lighting from Street View images
5. Calculate weighted safety score (0-100)
6. Classify route and suggest alternatives if needed
7. Cache result for 1 hour
8. Return scored routes to client

**SOS Activation Flow**:
1. User taps SOS button
2. Client sends SOS activation request
3. SOS Service creates geofence at user location
4. Query nearby devices using Redis GEORADIUS (50m)
5. Send push notifications to nearby devices
6. Send SMS/push to emergency contacts
7. Start location tracking (5-second intervals)
8. Enable radar interface with nearby device positions
9. Optional: Start video streaming to cloud storage

## Components and Interfaces

### Mobile Client Components

**SafeMapView**:
- Displays Google Maps with current location
- Renders crowd density heatmap overlay
- Provides search interface for destinations
- Shows route options with safety scores
- Handles route selection and navigation

**SOSRadarView**:
- Circular radar interface showing nearby devices
- Real-time position updates every 5 seconds
- Device selection for reporting
- Video recording controls
- Deactivation button

**ProfileView**:
- Displays trust score and classification
- Shows safety statistics (SOS count, assists, reports)
- Manages emergency contacts
- Displays safety badge (Bronze/Silver/Gold)

**LocationService**:
- Background service for location pings
- Handles online/offline queue management
- Implements exponential backoff for failures
- Respects battery optimization settings

### Backend Service Interfaces

**Telemetry Service API**:

```python
POST /api/v1/telemetry/ping
Request:
{
  "device_id": "uuid",
  "latitude": float,
  "longitude": float,
  "timestamp": "ISO8601",
  "accuracy": float  # meters
}
Response:
{
  "status": "success",
  "next_ping_interval": int  # seconds
}
```

**Route Analyzer API**:

```python
POST /api/v1/routes/analyze
Request:
{
  "origin": {"lat": float, "lng": float},
  "destination": {"lat": float, "lng": float},
  "time_of_day": "day|night",
  "alternatives": int  # number of alternative routes
}
Response:
{
  "routes": [
    {
      "route_id": "string",
      "polyline": "encoded_polyline",
      "safety_score": int,  # 0-100
      "risk_classification": "SAFE|MEDIUM|HIGH_RISK",
      "factors": {
        "crime_score": float,
        "crowd_score": float,
        "commercial_score": float,
        "lighting_score": float
      },
      "duration": int,  # seconds
      "distance": int   # meters
    }
  ],
  "recommended_route_id": "string"
}
```

**SOS Service API**:

```python
POST /api/v1/sos/activate
Request:
{
  "user_id": "uuid",
  "location": {"lat": float, "lng": float},
  "enable_video": bool
}
Response:
{
  "sos_id": "uuid",
  "geofence_radius": int,  # meters
  "video_stream_url": "string|null"
}

GET /api/v1/sos/radar?sos_id={uuid}
Response:
{
  "nearby_devices": [
    {
      "device_id": "anonymized_id",
      "relative_distance": float,  # meters
      "relative_bearing": float,   # degrees
      "last_seen": "ISO8601"
    }
  ],
  "update_interval": int  # seconds
}

POST /api/v1/sos/deactivate
Request:
{
  "sos_id": "uuid",
  "reason": "resolved|false_alarm"
}
Response:
{
  "status": "success",
  "trust_score_adjustment": int
}
```

**Incident Reporting API**:

```python
POST /api/v1/report/suspect
Request:
{
  "reporter_id": "uuid",
  "suspect_device_id": "string",
  "incident_type": "SOS_Trigger|Harassment|Poor_Lighting",
  "location": {"lat": float, "lng": float},
  "evidence_urls": ["string"],
  "description": "string"
}
Response:
{
  "report_id": "uuid",
  "status": "submitted",
  "government_system_ref": "string"
}
```

**User Profile API**:

```python
GET /api/v1/user/profile
Response:
{
  "user_id": "uuid",
  "trust_score": int,
  "classification": "Normal|Suspected|Fraud",
  "safety_badge": "Bronze|Silver|Gold",
  "statistics": {
    "sos_activations": int,
    "assists_provided": int,
    "reports_filed_against": int,
    "false_alarms": int
  },
  "emergency_contacts": [
    {
      "contact_id": "uuid",
      "name": "string",
      "phone": "string"
    }
  ]
}
```

## Data Models

### PostgreSQL Schema

**users**:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number VARCHAR(15) UNIQUE NOT NULL,
  trust_score INTEGER DEFAULT 50 CHECK (trust_score >= 0 AND trust_score <= 100),
  classification VARCHAR(20) DEFAULT 'Normal' CHECK (classification IN ('Normal', 'Suspected', 'Fraud')),
  device_fingerprint VARCHAR(255) UNIQUE NOT NULL,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'flagged', 'banned')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_device_fingerprint ON users(device_fingerprint);
CREATE INDEX idx_users_trust_score ON users(trust_score);
```

**emergency_contacts**:
```sql
CREATE TABLE emergency_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100),
  phone_number VARCHAR(15) NOT NULL,
  priority INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_emergency_contacts_user_id ON emergency_contacts(user_id);
```

**incident_reports**:
```sql
CREATE TABLE incident_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID REFERENCES users(id),
  suspect_device_id VARCHAR(255),
  incident_type VARCHAR(50) CHECK (incident_type IN ('SOS_Trigger', 'Harassment', 'Poor_Lighting')),
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  description TEXT,
  evidence_urls TEXT[],
  government_system_ref VARCHAR(100),
  status VARCHAR(20) DEFAULT 'submitted',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_incident_reports_location ON incident_reports USING GIST(location);
CREATE INDEX idx_incident_reports_suspect ON incident_reports(suspect_device_id);
CREATE INDEX idx_incident_reports_created_at ON incident_reports(created_at);
```

**sos_events**:
```sql
CREATE TABLE sos_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  activation_location GEOGRAPHY(POINT, 4326) NOT NULL,
  deactivation_location GEOGRAPHY(POINT, 4326),
  geofence_radius INTEGER DEFAULT 50,
  video_stream_url TEXT,
  activated_at TIMESTAMP DEFAULT NOW(),
  deactivated_at TIMESTAMP,
  deactivation_reason VARCHAR(50),
  nearby_devices_snapshot JSONB
);

CREATE INDEX idx_sos_events_user_id ON sos_events(user_id);
CREATE INDEX idx_sos_events_activated_at ON sos_events(activated_at);
```

**route_risk_cache**:
```sql
CREATE TABLE route_risk_cache (
  route_hash VARCHAR(64) PRIMARY KEY,
  origin_location GEOGRAPHY(POINT, 4326) NOT NULL,
  destination_location GEOGRAPHY(POINT, 4326) NOT NULL,
  safety_score INTEGER CHECK (safety_score >= 0 AND safety_score <= 100),
  risk_classification VARCHAR(20),
  crime_score FLOAT,
  crowd_score FLOAT,
  commercial_score FLOAT,
  lighting_score FLOAT,
  polyline TEXT,
  last_updated TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);

CREATE INDEX idx_route_cache_expires ON route_risk_cache(expires_at);
```

**trust_score_events**:
```sql
CREATE TABLE trust_score_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  event_type VARCHAR(50) NOT NULL,
  score_change INTEGER NOT NULL,
  previous_score INTEGER,
  new_score INTEGER,
  related_entity_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trust_score_events_user_id ON trust_score_events(user_id);
```

### Redis Data Structures

**Location Pings** (Geospatial Set):
```
Key: "location_pings"
Type: Sorted Set (GEOADD)
Members: device_id
Score: geohash
TTL: 60 seconds per member
```

**Active SOS Geofences** (Geospatial Set):
```
Key: "sos_geofences"
Type: Sorted Set (GEOADD)
Members: sos_id
Score: geohash of SOS location
TTL: None (manually removed on deactivation)
```

**Crowd Density Zones** (Hash):
```
Key: "crowd_zones:{zone_id}"
Type: Hash
Fields:
  - device_count: integer
  - last_updated: timestamp
  - zone_bounds: "lat1,lng1,lat2,lng2"
TTL: 120 seconds
```

**Route Cache** (String):
```
Key: "route:{route_hash}"
Type: String (JSON)
Value: {safety_score, factors, classification}
TTL: 3600 seconds (1 hour)
```

## Safety Score Algorithm

### Weighted Calculation (Optimized for Indian Context)

```
Safety_Score = (Crowd_Density × 0.35) + (Crime_History × 0.30) + 
               (Commercial_Activity × 0.25) + (Lighting × 0.10)
```

**Rationale for Weight Adjustments:**
- **Crowd Density (35%)**: Increased from 30% because "safety in numbers" is critical in Indian urban contexts
- **Crime History (30%)**: Maintained at high priority for historical risk assessment
- **Commercial Activity (25%)**: Increased from 20% as "eyes on the street" from shops is crucial
- **Lighting (10%)**: Kept minimal as street lighting data can be unreliable

### Crime Score (0-100)

Uses inverse distance weighting to crime hotspots:

```python
def calculate_crime_score(route_segments, crime_hotspots):
    """
    Calculate crime risk score based on proximity to historical crime locations.
    Lower score = higher risk. Score is inverted at the end.
    """
    total_weight = 0
    weighted_risk = 0
    
    for segment in route_segments:
        segment_risk = 0
        for hotspot in crime_hotspots:
            distance = haversine_distance(segment.midpoint, hotspot.location)
            if distance < 1000:  # 1km radius
                # Inverse distance: closer = higher risk
                weight = 1 / (distance + 1)
                risk = hotspot.severity * weight  # severity: 0-100
                segment_risk += risk
        
        # Normalize to 0-100 range
        segment_risk = min(segment_risk, 100)
        total_weight += segment.length
        weighted_risk += segment_risk * segment.length
    
    # Invert: high crime = low score
    crime_score = 100 - (weighted_risk / total_weight)
    return crime_score
```

### Crowd Score (0-100) - PRIMARY SAFETY INDICATOR

Based on real-time device density from Redis GEORADIUS:

```python
def calculate_crowd_score(route_segments, redis_client):
    """
    Calculate crowd density score using live location pings from Redis.
    Higher device count = higher safety score (safety in numbers).
    Query radius: 50m for precise crowd detection.
    """
    total_length = sum(seg.length for seg in route_segments)
    weighted_density = 0
    
    for segment in route_segments:
        # Query devices within 50m of segment (tighter radius for accuracy)
        devices = redis_client.georadius(
            "location_pings",
            segment.midpoint.lng,
            segment.midpoint.lat,
            50,  # Reduced from 100m for more precise crowd detection
            unit='m'
        )
        
        # Normalize density: 0 devices = 0, 20+ devices = 100
        density_score = min((len(devices) / 20) * 100, 100)
        weighted_density += density_score * segment.length
    
    crowd_score = weighted_density / total_length
    return crowd_score
```

### Commercial Score (0-100)

Based on open businesses ("Eyes on the Street" principle):

```python
def calculate_commercial_score(route_segments, google_places_api):
    """
    Calculate commercial activity score based on open shops/establishments.
    More open businesses = more witnesses = higher safety.
    """
    total_length = sum(seg.length for seg in route_segments)
    weighted_commercial = 0
    
    for segment in route_segments:
        # Query open businesses within 200m
        places = google_places_api.nearby_search(
            location=segment.midpoint,
            radius=200,
            open_now=True,
            type='establishment'
        )
        
        # Normalize: 0 places = 0, 10+ places = 100
        commercial_score = min((len(places) / 10) * 100, 100)
        weighted_commercial += commercial_score * segment.length
    
    return weighted_commercial / total_length
```

### Lighting Score (0-100)

Using computer vision on Street View images:

```python
def calculate_lighting_score(route_segments, street_view_api):
    total_length = sum(seg.length for seg in route_segments)
    weighted_lighting = 0
    
    for segment in route_segments:
        # Fetch Street View image
        image = street_view_api.get_image(
            location=segment.midpoint,
            heading=segment.bearing,
            size="640x640"
        )
        
        # Analyze brightness using OpenCV
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Normalize: 0-255 brightness to 0-100 score
        lighting_score = (mean_brightness / 255) * 100
        weighted_lighting += lighting_score * segment.length
    
    return weighted_lighting / total_length
```

### Risk Classification

```python
def classify_route(safety_score):
    if safety_score > 70:
        return "SAFE"
    elif safety_score >= 40:
        return "MEDIUM"
    else:
        return "HIGH_RISK"
```

## Trust Score Management

### Score Adjustment Rules

```python
TRUST_SCORE_ADJUSTMENTS = {
    "reported_during_sos": -10,
    "assisted_during_sos": +5,
    "false_alarm": -15,
    "verified_help": +10,
    "multiple_reports": -20,  # 3+ reports in 30 days
    "clean_record_bonus": +5   # No incidents for 90 days
}

def update_trust_score(user_id, event_type):
    user = get_user(user_id)
    adjustment = TRUST_SCORE_ADJUSTMENTS.get(event_type, 0)
    
    previous_score = user.trust_score
    new_score = max(0, min(100, previous_score + adjustment))
    
    user.trust_score = new_score
    user.classification = classify_user(new_score)
    
    log_trust_score_event(
        user_id=user_id,
        event_type=event_type,
        score_change=adjustment,
        previous_score=previous_score,
        new_score=new_score
    )
    
    if user.classification == "Fraud":
        flag_for_review(user_id)
    
    return new_score

def classify_user(trust_score):
    if trust_score == 0:
        return "Fraud"
    elif trust_score <= 30:
        return "Suspected"
    else:
        return "Normal"
```

### Fraud Detection

```python
def check_fraud_patterns(user_id):
    # Check for suspicious patterns
    recent_reports = get_reports_against_user(user_id, days=30)
    
    if len(recent_reports) >= 3:
        update_trust_score(user_id, "multiple_reports")
    
    # Check for false alarm pattern
    sos_events = get_user_sos_events(user_id, days=30)
    false_alarms = [e for e in sos_events if e.reason == "false_alarm"]
    
    if len(false_alarms) >= 2:
        update_trust_score(user_id, "false_alarm")
```

## Privacy Preservation

### Zone-Based Aggregation

```python
ZONE_SIZE = 100  # meters
MIN_DEVICES_PER_ZONE = 5

def aggregate_location_pings():
    # Get all active pings from Redis
    all_pings = redis_client.zrange("location_pings", 0, -1, withscores=True)
    
    # Group into geographic zones
    zones = defaultdict(list)
    for device_id, geohash in all_pings:
        lat, lng = decode_geohash(geohash)
        zone_id = get_zone_id(lat, lng, ZONE_SIZE)
        zones[zone_id].append(device_id)
    
    # Filter zones with insufficient devices
    aggregated_zones = {}
    for zone_id, devices in zones.items():
        if len(devices) >= MIN_DEVICES_PER_ZONE:
            aggregated_zones[zone_id] = {
                "device_count": len(devices),
                "zone_bounds": get_zone_bounds(zone_id),
                "last_updated": datetime.now().isoformat()
            }
        else:
            # Merge with adjacent zones
            adjacent_zone = find_adjacent_zone(zone_id, zones)
            if adjacent_zone:
                zones[adjacent_zone].extend(devices)
    
    # Store aggregated data
    for zone_id, data in aggregated_zones.items():
        redis_client.hset(f"crowd_zones:{zone_id}", mapping=data)
        redis_client.expire(f"crowd_zones:{zone_id}", 120)
    
    return aggregated_zones
```

### Anonymization

```python
def anonymize_device_id(device_id):
    # Use HMAC for consistent anonymization
    secret = get_daily_secret()  # Rotates daily
    return hmac.new(secret, device_id.encode(), hashlib.sha256).hexdigest()[:16]

def get_radar_devices(sos_location, radius=50):
    # Query nearby devices
    nearby = redis_client.georadius(
        "location_pings",
        sos_location.lng,
        sos_location.lat,
        radius,
        unit='m',
        withdist=True,
        withcoord=True
    )
    
    # Return anonymized data
    return [
        {
            "device_id": anonymize_device_id(device_id),
            "relative_distance": distance,
            "relative_bearing": calculate_bearing(sos_location, coords),
            "last_seen": datetime.now().isoformat()
        }
        for device_id, distance, coords in nearby
    ]
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Safety Score Range Invariant

*For any* route analyzed by the system, the calculated Safety_Score must be between 0 and 100 inclusive.

**Validates: Requirements 1.1**

### Property 2: Safety Score Weighted Calculation

*For any* set of factor scores (crime_score, crowd_score, commercial_score, lighting_score), the Safety_Score must equal (crime_score × 0.4) + (crowd_score × 0.3) + (commercial_score × 0.2) + (lighting_score × 0.1).

**Validates: Requirements 1.2**

### Property 3: High-Risk Routes Provide Alternatives

*For any* route with Safety_Score below 40, the system must suggest at least one alternative route with a higher Safety_Score.

**Validates: Requirements 1.6**

### Property 4: Inverse Distance Weighting for Crime

*For any* route segment and two crime hotspots at different distances, the hotspot closer to the segment must have a greater impact on the crime score than the farther hotspot.

**Validates: Requirements 1.7**

### Property 5: Location Ping Interval

*For any* active application session with location sharing enabled, Location_Pings must be sent at intervals between 30 and 60 seconds.

**Validates: Requirements 2.1**

### Property 6: Location Ping TTL

*For any* Location_Ping stored in the system, it must be automatically deleted after 60 seconds.

**Validates: Requirements 2.2, 9.4**

### Property 7: Zone-Based Aggregation

*For any* set of Location_Pings, the aggregation process must assign each ping to exactly one geographic zone.

**Validates: Requirements 2.3**

### Property 8: Privacy-Preserving Display

*For any* crowd density display output, it must contain zone-level aggregate data and must not contain individual device coordinates or identifiable information.

**Validates: Requirements 2.4, 9.2**

### Property 9: Location Sharing Termination

*For any* user who disables location sharing, the system must immediately stop sending Location_Pings from that device.

**Validates: Requirements 2.8**

### Property 10: SOS Activation Performance

*For any* SOS button tap, the system must activate SOS_Mode within 2 seconds.

**Validates: Requirements 3.1, 14.3**

### Property 11: Emergency Contact Alert Delivery

*For any* SOS activation, all configured Emergency_Contacts must receive an alert containing the user's current location and timestamp.

**Validates: Requirements 3.2, 11.5**

### Property 12: Geofence Notification Delivery

*For any* SOS activation, all devices within 50 meters of the SOS location must receive a "You are acting Suspicious" notification.

**Validates: Requirements 3.3**

### Property 13: Geofence Radius Invariant

*For any* SOS activation, the created Geofence must have exactly a 50-meter radius.

**Validates: Requirements 3.4**

### Property 14: SOS Location Update Frequency

*For any* active SOS_Mode session, user location updates must be sent every 5 seconds.

**Validates: Requirements 3.5**

### Property 15: SOS Deactivation Cleanup

*For any* SOS deactivation, the system must stop sending alerts and remove the associated Geofence.

**Validates: Requirements 3.6**

### Property 16: SOS Alert Content Completeness

*For any* SOS alert sent to an Emergency_Contact, the alert must contain both the user's current location and a timestamp.

**Validates: Requirements 3.7**

### Property 17: Radar Device Discovery

*For any* active SOS_Mode, the Radar_Interface must display all devices currently within the Geofence.

**Validates: Requirements 4.1**

### Property 18: Radar Coordinate Transformation

*For any* device displayed on the Radar_Interface, the system must show accurate relative distance (in meters) and bearing (in degrees) from the SOS user's location.

**Validates: Requirements 4.2**

### Property 19: Radar Device Entry Detection

*For any* device that enters a Geofence, it must appear on the Radar_Interface within 5 seconds.

**Validates: Requirements 4.3**

### Property 20: Radar Device Exit Detection

*For any* device that exits a Geofence, it must be removed from the Radar_Interface within 5 seconds.

**Validates: Requirements 4.4**

### Property 21: Radar Refresh Rate

*For any* active SOS_Mode session, the Radar_Interface must refresh device positions every 5 seconds.

**Validates: Requirements 4.6**

### Property 22: Radar Anonymization

*For any* device displayed on the Radar_Interface, the display must show an anonymized identifier and must not show personal information (name, phone number, user ID).

**Validates: Requirements 4.7**

### Property 23: Trust Score Adjustment Correctness

*For any* trust score event (reported_during_sos: -10, assisted_during_sos: +5, false_alarm: -15), the user's Trust_Score must change by exactly the specified delta.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 24: Trust Score Bounds Invariant

*For any* trust score update operation, the resulting Trust_Score must be between 0 and 100 inclusive (clamped at boundaries).

**Validates: Requirements 5.8**

### Property 25: Fraud Classification Trigger

*For any* user whose Trust_Score reaches 0, the system must classify them as "Fraud" and flag their account for review.

**Validates: Requirements 5.9**

### Property 26: Incident Report Creation Completeness

*For any* suspect device report, the system must create an incident report containing timestamp, geolocation, reporter_id, and suspect_device_id.

**Validates: Requirements 6.1, 6.4**

### Property 27: Evidence Attachment

*For any* incident report with attached evidence files, the system must store the evidence and maintain the association with the report.

**Validates: Requirements 6.2, 6.3**

### Property 28: Government System Integration

*For any* submitted incident report, the system must send it to Government_System integration endpoints.

**Validates: Requirements 6.5**

### Property 29: Incident Type Validation

*For any* incident report submission, the system must accept only valid incident types (SOS_Trigger, Harassment, Poor_Lighting) and reject invalid types.

**Validates: Requirements 6.6**

### Property 30: Video Stream Upload

*For any* active live streaming session, video data must be continuously uploaded to secure cloud storage.

**Validates: Requirements 7.2**

### Property 31: Video Stream URL Notification

*For any* active live streaming session, the stream URL must be sent to all Emergency_Contacts.

**Validates: Requirements 7.3**

### Property 32: Video Stream Termination and Persistence

*For any* SOS deactivation with active video streaming, the system must stop the stream and save the complete recording.

**Validates: Requirements 7.5**

### Property 33: Video Buffering and Delayed Upload

*For any* video streaming session with poor network connectivity, the system must buffer video locally and upload buffered content when connectivity improves.

**Validates: Requirements 7.6**

### Property 34: Video Evidence Attachment

*For any* completed video recording, the system must attach it as evidence to the associated incident report.

**Validates: Requirements 7.7**

### Property 35: Route Retrieval from Google Maps

*For any* destination search, the system must query Google Maps Directions API and retrieve at least one possible route.

**Validates: Requirements 8.2**

### Property 36: Safety Score Display on Routes

*For any* set of retrieved routes, the system must display each route with its calculated Safety_Score overlay.

**Validates: Requirements 8.3**

### Property 37: Street View Image Fetching

*For any* route being evaluated for lighting conditions, the system must fetch Street View Static API images for route segments.

**Validates: Requirements 8.4**

### Property 38: Google Places Query for Commercial Activity

*For any* route being evaluated for commercial activity, the system must query Google Places API for nearby open businesses.

**Validates: Requirements 8.5**

### Property 39: Minimum Zone Size Enforcement

*For any* geographic zone created during aggregation, the zone must have a radius of at least 100 meters.

**Validates: Requirements 9.1**

### Property 40: Location Ping Anonymization

*For any* Location_Ping stored in the system, it must use an anonymized identifier that is separate from the user's profile ID.

**Validates: Requirements 9.3**

### Property 41: Small Zone Merging

*For any* zone containing fewer than 5 devices, the system must merge it with adjacent zones before displaying crowd density.

**Validates: Requirements 9.5**

### Property 42: Location Data Retention Limit

*For any* point in time, the system must not store location data older than 60 seconds for crowd density purposes.

**Validates: Requirements 9.6**

### Property 43: SOS Location Sharing Scope

*For any* active SOS_Mode, precise location data must be shared only with Emergency_Contacts and devices within the Geofence, and not with other users.

**Validates: Requirements 9.7**

### Property 44: Profile Statistics Accuracy

*For any* user profile display, the statistics (SOS activations count, assists count, reports filed against count) must accurately reflect the user's historical events.

**Validates: Requirements 10.3, 10.4, 10.5**

### Property 45: Profile Update Latency

*For any* Trust_Score change, the profile display must reflect the updated score within 10 seconds.

**Validates: Requirements 10.7**

### Property 46: Emergency Contact Capacity Limit

*For any* user, the system must allow adding up to 5 Emergency_Contacts and must reject attempts to add more than 5.

**Validates: Requirements 11.2**

### Property 47: Emergency Contact Required Fields

*For any* Emergency_Contact addition, the system must require a phone number and must accept an optional name.

**Validates: Requirements 11.3**

### Property 48: Emergency Contact Persistence

*For any* Emergency_Contact update operation, the system must save changes immediately and persistently.

**Validates: Requirements 11.4**

### Property 49: Emergency Contact Deletion

*For any* Emergency_Contact removal, the system must allow deletion at any time and must not send future SOS alerts to the removed contact.

**Validates: Requirements 11.6, 11.7**

### Property 50: Crime Data Query Radius

*For any* route safety calculation, the system must query Government_System for crime data within exactly 1 kilometer radius of the route.

**Validates: Requirements 12.1**

### Property 51: Incident Report Submission Latency

*For any* incident report submission, the system must send it to Government_System within 30 seconds.

**Validates: Requirements 12.2**

### Property 52: Government System Fallback

*For any* Government_System API failure, the system must calculate Safety_Score using cached data and log the failure.

**Validates: Requirements 12.3**

### Property 53: Government System Authentication

*For any* Government_System API request, the system must include secure API credentials for authentication.

**Validates: Requirements 12.4**

### Property 54: Crime Data Filtering

*For any* crime data received from Government_System, the system must filter to include only rape and sexual assault cases from the past 12 months.

**Validates: Requirements 12.5**

### Property 55: Crime Data Cache Duration

*For any* crime data fetched from Government_System, the system must cache it for exactly 24 hours before requiring a refresh.

**Validates: Requirements 12.6**

### Property 56: Government System Retry Logic

*For any* Government_System API error, the system must retry up to 3 times with exponential backoff before failing.

**Validates: Requirements 12.7**

### Property 57: Device Fingerprint Uniqueness

*For any* application installation, the system must generate a unique device_fingerprint that is different from all existing fingerprints.

**Validates: Requirements 13.1**

### Property 58: Device Fingerprint Consistent Usage

*For any* device, the system must use the same device_fingerprint consistently across Radar_Interface displays, incident reports, and all other device identification scenarios.

**Validates: Requirements 13.2, 13.3**

### Property 59: Device Fingerprint Data Separation

*For any* stored device_fingerprint, it must be stored in a separate table/field from personally identifiable information (name, phone, email).

**Validates: Requirements 13.4**

### Property 60: Device Fingerprint Regeneration on Reinstall

*For any* application reinstallation, the system must generate a new device_fingerprint that is different from the previous fingerprint.

**Validates: Requirements 13.5**

### Property 61: Dual Authentication Requirement

*For any* API request, the system must require both valid user credentials and a valid device_fingerprint for authentication.

**Validates: Requirements 13.6**

### Property 62: Fraud Device Access Restriction

*For any* device_fingerprint associated with a user classified as "Fraud", the system must restrict that device's access to the application.

**Validates: Requirements 13.7**

### Property 63: Safety Score Calculation Performance

*For any* route analysis request, the system must return the Safety_Score within 3 seconds.

**Validates: Requirements 14.2**

### Property 64: Asynchronous Incident Report Processing

*For any* incident report submission, the system must use asynchronous processing such that the user request completes without blocking on report storage.

**Validates: Requirements 14.5**

### Property 65: SOS Request Prioritization

*For any* system state with both SOS requests and route analysis requests in queue, the system must process SOS requests before route analysis requests.

**Validates: Requirements 14.7**

### Property 66: Offline SOS Activation

*For any* SOS button tap when network connectivity is unavailable, the system must allow SOS_Mode activation using cached data.

**Validates: Requirements 15.1**

### Property 67: Offline Location Ping Queuing

*For any* Location_Ping generated while offline, the system must queue it locally and send it when connectivity is restored.

**Validates: Requirements 15.2**

### Property 68: Stale Data Indication

*For any* crowd density display while offline, the system must show the last known data with a visible staleness indicator.

**Validates: Requirements 15.3**

### Property 69: Offline Route Cache Access

*For any* route previously calculated, the system must allow viewing its Safety_Score from cache while offline.

**Validates: Requirements 15.4**

### Property 70: Offline SMS Fallback

*For any* SOS activation while offline, the system must attempt to send SMS alerts to Emergency_Contacts as a fallback.

**Validates: Requirements 15.5**

### Property 71: Map Tile Caching

*For any* user's current geographic area, the system must cache map tiles for offline viewing.

**Validates: Requirements 15.6**

### Property 72: Data Synchronization on Reconnection

*For any* network connectivity restoration, the system must synchronize all queued data (location pings, reports, updates) within 30 seconds.

**Validates: Requirements 15.7**

## Error Handling

### Client-Side Error Handling

**Network Failures**:
- Location ping failures: Queue locally, retry with exponential backoff (1s, 2s, 4s, 8s, max 60s)
- Route analysis failures: Display cached routes if available, show error message if no cache
- SOS activation failures: Fall back to SMS alerts, display warning to user
- Video streaming failures: Buffer locally, attempt upload when connectivity improves

**GPS/Location Errors**:
- GPS unavailable: Prompt user to enable location services, disable location-dependent features
- Low accuracy (>100m): Display warning, continue with degraded accuracy
- Location permission denied: Show explanation dialog, disable safety features requiring location

**API Errors**:
- Google Maps API failures: Use cached map tiles, display "offline mode" indicator
- Government System failures: Use cached crime data, log failure for retry
- Rate limiting: Implement exponential backoff, queue requests

**User Input Errors**:
- Invalid phone number format: Display inline validation error, prevent submission
- Empty required fields: Highlight fields, show error message
- File upload failures: Retry upload, allow user to retry manually

### Server-Side Error Handling

**Database Errors**:
- Connection failures: Retry with connection pool, return 503 Service Unavailable if exhausted
- Query timeouts: Log slow queries, return partial results if possible
- Constraint violations: Return 400 Bad Request with specific error message
- Deadlocks: Automatic retry up to 3 times with random jitter

**Redis Errors**:
- Connection failures: Fall back to database queries, log error for monitoring
- Memory exhaustion: Implement LRU eviction, alert operations team
- Cluster node failures: Automatic failover to replica nodes

**External API Errors**:
- Google Maps API errors: Return cached data, log error, retry with backoff
- Government System errors: Use cached data, queue report for later submission
- Authentication failures: Refresh credentials, alert operations team
- Rate limit exceeded: Implement request queuing, use cached data

**Validation Errors**:
- Invalid coordinates: Return 400 Bad Request with error details
- Invalid device fingerprint: Return 401 Unauthorized, require re-authentication
- Invalid trust score adjustment: Log error, skip adjustment, alert monitoring
- Malformed request body: Return 400 Bad Request with JSON schema validation errors

**Resource Exhaustion**:
- High CPU usage: Implement request throttling, prioritize SOS requests
- High memory usage: Trigger garbage collection, scale horizontally
- Disk space low: Archive old incident reports, alert operations team
- Connection pool exhausted: Queue requests, return 503 if queue full

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field",
      "reason": "validation_failed"
    },
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

### Logging and Monitoring

**Error Logging**:
- All errors logged with severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include request_id for tracing across services
- Log stack traces for 500-level errors
- Sanitize PII from logs (phone numbers, locations)

**Monitoring Alerts**:
- SOS activation failures: Immediate alert (critical)
- Database connection failures: Alert within 1 minute (critical)
- Government System unavailable: Alert within 5 minutes (high)
- High error rate (>5%): Alert within 5 minutes (high)
- Slow response times (>3s): Alert within 10 minutes (medium)

## Testing Strategy

### Dual Testing Approach

The NIRBHAYA application requires both unit testing and property-based testing to ensure comprehensive coverage. These approaches are complementary:

- **Unit tests** verify specific examples, edge cases, and error conditions
- **Property tests** verify universal properties across all inputs

Together, they provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness.

### Property-Based Testing

**Framework**: Use Hypothesis (Python) for property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: nirbhaya-safety-app, Property {number}: {property_text}`

**Property Test Examples**:

```python
from hypothesis import given, strategies as st
import hypothesis.strategies as st

# Property 1: Safety Score Range Invariant
@given(
    crime_score=st.floats(min_value=0, max_value=100),
    crowd_score=st.floats(min_value=0, max_value=100),
    commercial_score=st.floats(min_value=0, max_value=100),
    lighting_score=st.floats(min_value=0, max_value=100)
)
def test_safety_score_range_invariant(crime_score, crowd_score, commercial_score, lighting_score):
    # Feature: nirbhaya-safety-app, Property 1: Safety Score Range Invariant
    safety_score = calculate_safety_score(crime_score, crowd_score, commercial_score, lighting_score)
    assert 0 <= safety_score <= 100

# Property 24: Trust Score Bounds Invariant
@given(
    initial_score=st.integers(min_value=0, max_value=100),
    adjustment=st.integers(min_value=-50, max_value=50)
)
def test_trust_score_bounds_invariant(initial_score, adjustment):
    # Feature: nirbhaya-safety-app, Property 24: Trust Score Bounds Invariant
    user = User(trust_score=initial_score)
    update_trust_score(user, adjustment)
    assert 0 <= user.trust_score <= 100

# Property 8: Privacy-Preserving Display
@given(
    location_pings=st.lists(
        st.tuples(
            st.floats(min_value=-90, max_value=90),  # latitude
            st.floats(min_value=-180, max_value=180)  # longitude
        ),
        min_size=10,
        max_size=1000
    )
)
def test_privacy_preserving_display(location_pings):
    # Feature: nirbhaya-safety-app, Property 8: Privacy-Preserving Display
    crowd_density = aggregate_location_pings(location_pings)
    
    # Verify output contains zone data
    assert "zones" in crowd_density
    
    # Verify no individual coordinates in output
    output_str = json.dumps(crowd_density)
    for lat, lng in location_pings:
        assert str(lat) not in output_str
        assert str(lng) not in output_str
```

### Unit Testing

**Framework**: Use pytest (Python) for unit testing

**Coverage Requirements**:
- Minimum 80% code coverage for core business logic
- 100% coverage for safety-critical components (SOS, trust score, privacy)

**Unit Test Focus Areas**:

1. **Edge Cases**:
   - Risk classification boundaries (scores of 39, 40, 70, 71)
   - Trust score boundaries (0, 1, 30, 31, 100)
   - Empty input handling (no routes, no devices, no contacts)
   - Maximum capacity limits (5 emergency contacts, geofence radius)

2. **Error Conditions**:
   - Network failures during SOS activation
   - Invalid coordinates (out of range, NaN)
   - Malformed API responses
   - Database connection failures
   - Authentication failures

3. **Integration Points**:
   - Google Maps API integration
   - Government System API integration
   - Redis geospatial queries
   - PostgreSQL PostGIS queries
   - SMS/push notification delivery

4. **Specific Examples**:
   - New user registration (trust score = 50)
   - First-time app launch (emergency contact prompt)
   - SOS activation with video enabled
   - Route with zero crowd density
   - Device entering/exiting geofence

**Example Unit Tests**:

```python
def test_new_user_default_trust_score():
    """Test that new users start with trust score of 50"""
    user = create_user(phone_number="+1234567890")
    assert user.trust_score == 50
    assert user.classification == "Normal"

def test_high_risk_route_classification():
    """Test that routes with score < 40 are classified as HIGH_RISK"""
    route = Route(safety_score=35)
    assert classify_route(route) == "HIGH_RISK"

def test_emergency_contact_limit():
    """Test that users cannot add more than 5 emergency contacts"""
    user = create_user(phone_number="+1234567890")
    
    # Add 5 contacts successfully
    for i in range(5):
        add_emergency_contact(user, phone=f"+123456789{i}")
    
    # 6th contact should fail
    with pytest.raises(ValidationError, match="Maximum 5 contacts"):
        add_emergency_contact(user, phone="+9999999999")

def test_sos_activation_without_network():
    """Test that SOS can activate offline using cached data"""
    user = create_user(phone_number="+1234567890")
    
    # Simulate offline state
    with mock_network_unavailable():
        sos_event = activate_sos(user, location=(37.7749, -122.4194))
        
        assert sos_event.status == "active"
        assert sos_event.offline_mode == True
```

### Integration Testing

**Focus**: Test interactions between components

**Key Integration Tests**:
1. End-to-end route analysis (API → Route Analyzer → Google Maps → Database → Cache)
2. SOS activation flow (Mobile → API → SOS Service → Redis → Notifications)
3. Location ping processing (Mobile → Telemetry → Redis → Aggregation → WebSocket)
4. Incident reporting (Mobile → API → Database → Government System)
5. Trust score updates (Event → Trust Manager → Database → Profile Update)

### Performance Testing

**Load Testing**:
- Simulate 10,000 concurrent location pings per second
- Measure route analysis response time under load
- Test SOS activation latency with 1000 concurrent activations

**Stress Testing**:
- Test system behavior at 2x expected load
- Identify breaking points and failure modes
- Verify graceful degradation

**Benchmarks**:
- Location ping processing: < 50ms per ping
- Route analysis: < 3 seconds
- SOS activation: < 2 seconds
- Geospatial queries: < 100ms
- Trust score updates: < 200ms

### Security Testing

**Penetration Testing**:
- Test authentication bypass attempts
- Test SQL injection vulnerabilities
- Test XSS vulnerabilities in mobile app
- Test API rate limiting effectiveness

**Privacy Testing**:
- Verify location data anonymization
- Test that PII is not leaked in logs
- Verify data retention policies are enforced
- Test that deleted data is truly removed

### Mobile Testing

**Device Testing**:
- Test on Android 8.0+ and iOS 13.0+
- Test on various screen sizes and resolutions
- Test with different GPS accuracy levels
- Test battery impact of background location tracking

**Offline Testing**:
- Test all offline functionality
- Verify data synchronization on reconnection
- Test queue management for offline operations
- Verify cache expiration and refresh

### Continuous Integration

**CI Pipeline**:
1. Run unit tests on every commit
2. Run property tests on every pull request
3. Run integration tests on merge to main
4. Run performance tests nightly
5. Generate coverage reports
6. Fail build if coverage drops below 80%

**Test Execution Time**:
- Unit tests: < 5 minutes
- Property tests: < 15 minutes
- Integration tests: < 30 minutes
- Full test suite: < 1 hour
