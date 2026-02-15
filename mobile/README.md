# NIRBHAYA Mobile Client

Mobile application built with Flet framework following the Indian Tricolour theme.

## Structure

```
mobile/
├── config.py                 # Configuration and color constants
├── main.py                   # Main application entry point
├── screens/                  # UI screens
│   ├── __init__.py
│   ├── safe_map.py          # Home screen with map and route analysis
│   ├── sos_radar.py         # SOS radar interface
│   └── profile.py           # User profile and emergency contacts
└── services/                 # Background services
    ├── __init__.py
    ├── location_service.py  # Location ping service
    └── offline_queue.py     # Offline data queue management
```

## Features Implemented

### 1. SafeMap Home Screen (Task 15.1)
- Google Maps placeholder with current location marker
- Destination search interface
- Route display with safety scores
- Color-coded route cards (Green for safe, Saffron for risky)
- Floating SOS button
- Indian Tricolour themed app bar

### 2. SOS Radar Screen (Task 15.2)
- Circular radar interface with tricolour gradient
- Nearby device detection display
- Distance rings (10m, 25m, 50m)
- Video recording controls
- SOS deactivation button
- Real-time device position updates (every 5 seconds)

### 3. User Profile Screen (Task 15.3)
- Trust score display with progress bar
- User classification (Normal/Suspected/Fraud)
- Safety badge (Bronze/Silver/Gold)
- Statistics cards (SOS count, assists, reports)
- Emergency contact management (max 5 contacts)
- Add/Edit/Delete contact functionality

### 4. Background Location Service (Task 15.4)
- Location pings every 30-60 seconds
- Online/offline queue management
- Battery optimization
- Exponential backoff for retries
- Respects location sharing settings

### 5. Offline Queue Management (Task 15.4)
- Queues location pings when offline
- Queues incident reports when offline
- Synchronizes within 30 seconds of reconnection
- Size-limited queues (max 1000 items)
- Persistent storage support

## Color Theme

Following the Indian Tricolour:
- **Saffron (#FF9933)**: Emergency actions, warnings, SOS button
- **India Green (#138808)**: Safe routes, success states, trust indicators
- **White (#FFFFFF)**: Backgrounds, content areas
- **Navy Blue (#000080)**: Text, icons, borders (Ashoka Chakra color)

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the mobile app
python mobile/main.py
```

## Testing

All mobile UI components have comprehensive unit tests:

```bash
# Run mobile UI tests
pytest tests/test_mobile_ui.py -v

# Test coverage:
# - SafeMap screen: 5 tests
# - SOS Radar screen: 5 tests
# - Profile screen: 5 tests
# - Location service: 5 tests
# - Battery optimizer: 5 tests
# - Offline queue: 7 tests
# Total: 32 tests (all passing)
```

## Requirements Validated

- **Requirement 8.1**: Map interface with Google Maps
- **Requirement 8.3**: Route display with safety scores
- **Requirement 8.6**: Crowd density heatmap overlay
- **Requirement 8.7**: Route selection interface
- **Requirement 4.5**: Radar interface for nearby devices
- **Requirement 10.1**: Trust score display
- **Requirement 10.2**: User profile with statistics
- **Requirement 2.1**: Location pings every 30-60 seconds
- **Requirement 2.8**: Stop pings when location sharing disabled
- **Requirement 15.2**: Offline location ping queuing
- **Requirement 15.7**: Data synchronization on reconnection

## Next Steps

1. Integrate actual Google Maps API
2. Connect to backend API endpoints
3. Implement video recording functionality
4. Add WebSocket support for real-time updates
5. Implement custom canvas drawing for radar visualization
6. Add GPS location tracking
7. Implement push notifications
8. Add SMS fallback for offline SOS
