# Requirements Document: NIRBHAYA Women's Safety Application

## Introduction

NIRBHAYA is a mobile-first safety application designed to enhance women's safety through intelligent route analysis, real-time crowd density tracking, and emergency response systems. The application transforms every installed device into a live sensor, creating a distributed network for safety monitoring while preserving user privacy. The system provides route safety scoring, SOS emergency features with radar-based nearby device detection, user trust scoring, and incident reporting capabilities.

## Glossary

- **System**: The NIRBHAYA mobile application and backend infrastructure
- **User**: Any person with the application installed on their mobile device
- **Device**: A mobile phone with the NIRBHAYA application installed
- **Sensor_Node**: A device actively sharing location data for crowd density tracking
- **Route_Analyzer**: The component that evaluates route safety based on multiple factors
- **Safety_Score**: A numerical value (0-100) indicating route safety level
- **Crowd_Mesh**: The distributed network of devices providing real-time crowd density data
- **SOS_Mode**: Emergency state activated when user triggers distress signal
- **Radar_Interface**: Visual display showing nearby devices during SOS mode
- **Trust_Score**: A numerical value (0-100) indicating user reliability and behavior
- **Suspect_Device**: A device reported as suspicious during an SOS event
- **Emergency_Contact**: Pre-configured contacts notified during SOS activation
- **Geofence**: A virtual perimeter (50m radius) around an SOS location
- **Location_Ping**: Periodic location update sent by a device (30-60 second intervals)
- **Crime_Hotspot**: Geographic area with historical crime data
- **Risk_Classification**: Categorization of routes as HIGH_RISK, MEDIUM, or SAFE
- **Evidence**: Media files (video/images) attached to incident reports
- **Government_System**: External systems for crime data and incident reporting integration

## Requirements

### Requirement 1: Route Safety Analysis

**User Story:** As a user, I want to analyze potential routes before traveling, so that I can choose the safest path to my destination.

#### Acceptance Criteria

1. WHEN a user selects a route, THE Route_Analyzer SHALL calculate a Safety_Score between 0 and 100
2. WHEN calculating Safety_Score, THE Route_Analyzer SHALL weight crime history at 40%, crowd density at 30%, commercial activity at 20%, and lighting conditions at 10%
3. WHEN a Safety_Score is below 40, THE System SHALL classify the route as HIGH_RISK
4. WHEN a Safety_Score is between 40 and 70, THE System SHALL classify the route as MEDIUM
5. WHEN a Safety_Score is above 70, THE System SHALL classify the route as SAFE
6. WHEN a route is classified as HIGH_RISK, THE System SHALL suggest at least one safer alternative route
7. WHEN evaluating crime history, THE Route_Analyzer SHALL use inverse distance weighting to Crime_Hotspots
8. WHEN evaluating crowd density, THE Route_Analyzer SHALL use real-time data from Crowd_Mesh
9. WHEN evaluating commercial activity, THE Route_Analyzer SHALL query open shops via Google Places API
10. WHEN evaluating lighting conditions, THE Route_Analyzer SHALL analyze Street View images using computer vision

### Requirement 2: Real-Time Crowd Density Tracking

**User Story:** As a user, I want to see real-time crowd density in different areas, so that I can avoid deserted locations and choose populated routes.

#### Acceptance Criteria

1. WHEN the application is active, THE System SHALL send Location_Ping every 30 to 60 seconds
2. WHEN a Location_Ping is received, THE System SHALL store it with a 60-second time-to-live
3. WHEN aggregating crowd density, THE System SHALL group Location_Pings into geographic zones
4. WHEN displaying crowd density, THE System SHALL show density zones without revealing individual user locations
5. WHEN a zone has zero Location_Pings for 60 seconds, THE System SHALL mark that zone as deserted
6. WHEN calculating route Safety_Score, THE System SHALL incorporate current crowd density data
7. THE System SHALL use Redis geospatial indexing for efficient location queries
8. WHEN a user disables location sharing, THE System SHALL stop sending Location_Pings immediately

### Requirement 3: SOS Emergency Activation

**User Story:** As a user in distress, I want to activate an emergency alert with one tap, so that I can quickly notify my contacts and nearby users.

#### Acceptance Criteria

1. WHEN a user taps the SOS button, THE System SHALL activate SOS_Mode within 2 seconds
2. WHEN SOS_Mode is activated, THE System SHALL send alerts to all Emergency_Contacts immediately
3. WHEN SOS_Mode is activated, THE System SHALL display "You are acting Suspicious" message on devices within the Geofence
4. WHEN SOS_Mode is activated, THE System SHALL create a Geofence with 50-meter radius around the user location
5. WHEN in SOS_Mode, THE System SHALL update user location every 5 seconds
6. WHEN SOS_Mode is deactivated, THE System SHALL stop sending alerts and remove the Geofence
7. WHEN SOS alert is sent, THE Emergency_Contact SHALL receive user's current location and timestamp

### Requirement 4: Radar Interface for Nearby Device Detection

**User Story:** As a user in SOS mode, I want to see nearby devices on a radar interface, so that I can identify and report suspicious individuals.

#### Acceptance Criteria

1. WHEN SOS_Mode is active, THE Radar_Interface SHALL display all devices within the Geofence
2. WHEN displaying devices, THE Radar_Interface SHALL show relative distance and direction from the user
3. WHEN a device enters the Geofence, THE Radar_Interface SHALL add it to the display within 5 seconds
4. WHEN a device exits the Geofence, THE Radar_Interface SHALL remove it from the display within 5 seconds
5. WHEN a user taps a device on the Radar_Interface, THE System SHALL allow reporting that device as suspicious
6. THE Radar_Interface SHALL refresh device positions every 5 seconds during SOS_Mode
7. WHEN displaying devices, THE System SHALL show anonymized identifiers, not personal information

### Requirement 5: User Trust Score System

**User Story:** As a system administrator, I want to maintain trust scores for all users, so that the system can identify and manage potentially fraudulent or malicious users.

#### Acceptance Criteria

1. WHEN a new user registers, THE System SHALL assign a Trust_Score of 50
2. WHEN a user is reported during SOS_Mode, THE System SHALL decrease their Trust_Score by 10 points
3. WHEN a user successfully assists during SOS_Mode, THE System SHALL increase their Trust_Score by 5 points
4. WHEN a user files a false SOS alarm, THE System SHALL decrease their Trust_Score by 15 points
5. WHEN Trust_Score reaches 0, THE System SHALL classify the user as Fraud
6. WHEN Trust_Score is between 1 and 30, THE System SHALL classify the user as Suspected
7. WHEN Trust_Score is above 30, THE System SHALL classify the user as Normal
8. THE System SHALL ensure Trust_Score never exceeds 100 or falls below 0
9. WHEN a user is classified as Fraud, THE System SHALL flag their account for review

### Requirement 6: Incident Reporting

**User Story:** As a user, I want to report suspicious devices and incidents with evidence, so that authorities can investigate and take appropriate action.

#### Acceptance Criteria

1. WHEN a user reports a Suspect_Device, THE System SHALL create an incident report with timestamp and geolocation
2. WHEN creating an incident report, THE System SHALL allow attaching Evidence files (images or video)
3. WHEN Evidence is attached, THE System SHALL store it securely with the incident report
4. WHEN an incident report is created, THE System SHALL tag it with the reporter's user ID and Suspect_Device ID
5. WHEN an incident report is submitted, THE System SHALL send it to Government_System integration endpoints
6. THE System SHALL support incident types: SOS_Trigger, Harassment, and Poor_Lighting
7. WHEN a report is filed against a device, THE System SHALL update the associated user's Trust_Score

### Requirement 7: Live Video Streaming for Evidence

**User Story:** As a user in distress, I want to optionally stream live video during SOS mode, so that I can provide real-time evidence of the situation.

#### Acceptance Criteria

1. WHERE live streaming is enabled, WHEN SOS_Mode is activated, THE System SHALL offer to start video recording
2. WHERE live streaming is active, THE System SHALL stream video to secure cloud storage
3. WHERE live streaming is active, THE System SHALL send the stream URL to Emergency_Contacts
4. WHEN video streaming starts, THE System SHALL display a recording indicator to the user
5. WHEN SOS_Mode is deactivated, THE System SHALL stop video streaming and save the recording
6. WHERE network connectivity is poor, THE System SHALL buffer video locally and upload when connection improves
7. WHEN video recording completes, THE System SHALL attach it as Evidence to the incident report

### Requirement 8: Google Maps Integration

**User Story:** As a user, I want to select routes and view safety information on a map interface, so that I can make informed decisions about my travel path.

#### Acceptance Criteria

1. WHEN a user opens the application, THE System SHALL display a map interface using Google Maps API
2. WHEN a user searches for a destination, THE System SHALL use Google Maps Directions API to retrieve possible routes
3. WHEN routes are retrieved, THE System SHALL display them on the map with Safety_Score overlays
4. WHEN evaluating lighting conditions, THE System SHALL fetch Street View Static API images for route segments
5. WHEN evaluating commercial activity, THE System SHALL query Google Places API for nearby open businesses
6. THE System SHALL display crowd density as a heatmap overlay on the map
7. WHEN a user selects a route, THE System SHALL highlight it and display detailed safety analysis

### Requirement 9: Privacy-Preserving Location Tracking

**User Story:** As a user, I want my location data to be used for crowd density without revealing my individual identity, so that my privacy is protected.

#### Acceptance Criteria

1. WHEN aggregating Location_Pings, THE System SHALL group them into geographic zones of at least 100-meter radius
2. WHEN displaying crowd density, THE System SHALL show zone-level aggregates, not individual device locations
3. WHEN storing Location_Pings, THE System SHALL use anonymized identifiers separate from user profiles
4. WHEN a Location_Ping expires (60 seconds), THE System SHALL delete it permanently
5. IF a zone contains fewer than 5 devices, THEN THE System SHALL merge it with adjacent zones before display
6. THE System SHALL not store historical location data beyond 60 seconds for crowd density purposes
7. WHEN in SOS_Mode, THE System SHALL temporarily share precise location only with Emergency_Contacts and within Geofence

### Requirement 10: User Profile and Safety Dashboard

**User Story:** As a user, I want to view my trust score and safety statistics, so that I can understand my standing in the system and track my safety activities.

#### Acceptance Criteria

1. WHEN a user opens their profile, THE System SHALL display their current Trust_Score
2. WHEN displaying Trust_Score, THE System SHALL show the user's classification (Normal, Suspected, or Fraud)
3. WHEN a user views their profile, THE System SHALL display the number of SOS activations they have made
4. WHEN a user views their profile, THE System SHALL display the number of times they have assisted others
5. WHEN a user views their profile, THE System SHALL display the number of reports filed against them
6. THE System SHALL display a safety badge based on Trust_Score ranges (Bronze: 30-50, Silver: 51-75, Gold: 76-100)
7. WHEN Trust_Score changes, THE System SHALL update the profile display within 10 seconds

### Requirement 11: Emergency Contact Management

**User Story:** As a user, I want to configure emergency contacts, so that the right people are notified when I activate SOS mode.

#### Acceptance Criteria

1. WHEN a user first installs the application, THE System SHALL prompt them to add at least one Emergency_Contact
2. THE System SHALL allow users to add up to 5 Emergency_Contacts
3. WHEN adding an Emergency_Contact, THE System SHALL require a phone number and optional name
4. WHEN a user updates Emergency_Contacts, THE System SHALL save changes immediately
5. WHEN SOS_Mode is activated, THE System SHALL send alerts to all configured Emergency_Contacts
6. THE System SHALL allow users to remove Emergency_Contacts at any time
7. WHEN an Emergency_Contact is removed, THE System SHALL not send future SOS alerts to that contact

### Requirement 12: Government System Integration

**User Story:** As a system administrator, I want to integrate with government crime databases and reporting systems, so that the application can access historical crime data and submit incident reports to authorities.

#### Acceptance Criteria

1. WHEN calculating Safety_Score, THE System SHALL query Government_System for historical crime data within 1-kilometer radius of the route
2. WHEN an incident report is submitted, THE System SHALL send it to Government_System integration endpoints within 30 seconds
3. WHEN Government_System data is unavailable, THE System SHALL calculate Safety_Score using cached data and log the failure
4. THE System SHALL authenticate with Government_System using secure API credentials
5. WHEN receiving crime data, THE System SHALL filter for rape and sexual assault cases from the past 12 months
6. THE System SHALL cache crime data for 24 hours to reduce API calls
7. WHEN Government_System returns an error, THE System SHALL retry up to 3 times with exponential backoff

### Requirement 13: Device Fingerprinting and Authentication

**User Story:** As a system administrator, I want to uniquely identify devices, so that the system can track suspicious behavior and prevent abuse.

#### Acceptance Criteria

1. WHEN a user installs the application, THE System SHALL generate a unique device_fingerprint
2. THE System SHALL use device_fingerprint to identify devices in Radar_Interface and incident reports
3. WHEN a device is reported multiple times, THE System SHALL associate all reports with the same device_fingerprint
4. THE System SHALL store device_fingerprint separately from personally identifiable information
5. WHEN a user reinstalls the application, THE System SHALL generate a new device_fingerprint
6. WHEN authenticating API requests, THE System SHALL require both user credentials and device_fingerprint
7. IF a device_fingerprint is associated with a Fraud classification, THEN THE System SHALL restrict that device's access

### Requirement 14: Scalability and Performance

**User Story:** As a system architect, I want the system to handle nationwide deployment, so that millions of users can use the application simultaneously without performance degradation.

#### Acceptance Criteria

1. WHEN processing Location_Pings, THE System SHALL handle at least 10,000 requests per second
2. WHEN calculating Safety_Score, THE System SHALL return results within 3 seconds
3. WHEN activating SOS_Mode, THE System SHALL send alerts within 2 seconds
4. THE System SHALL use Redis for geospatial queries to achieve sub-100ms query times
5. WHEN storing incident reports, THE System SHALL use asynchronous processing to avoid blocking user requests
6. THE System SHALL use database connection pooling to handle concurrent requests efficiently
7. WHEN the system experiences high load, THE System SHALL prioritize SOS_Mode requests over route analysis requests

### Requirement 15: Offline Functionality

**User Story:** As a user in an area with poor connectivity, I want basic safety features to work offline, so that I can still access critical functionality during emergencies.

#### Acceptance Criteria

1. WHEN network connectivity is unavailable, THE System SHALL allow SOS_Mode activation using cached data
2. WHEN offline, THE System SHALL queue Location_Pings and send them when connectivity is restored
3. WHEN offline, THE System SHALL display the last known crowd density data with a staleness indicator
4. WHEN offline, THE System SHALL allow viewing previously calculated route Safety_Scores from cache
5. WHEN offline and SOS_Mode is activated, THE System SHALL attempt to send SMS alerts to Emergency_Contacts
6. THE System SHALL cache map tiles for the user's current area for offline viewing
7. WHEN connectivity is restored, THE System SHALL synchronize all queued data within 30 seconds
