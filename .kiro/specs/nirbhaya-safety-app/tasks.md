# Implementation Plan: NIRBHAYA Women's Safety Application

## Overview

This implementation plan breaks down the NIRBHAYA safety application into discrete coding tasks. The approach follows an incremental development strategy: starting with core infrastructure, then building the telemetry and crowd density system, followed by route analysis, SOS features, trust scoring, and finally integration and testing. Each task builds on previous work, ensuring no orphaned code.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create Python project with FastAPI backend and Flet mobile client
  - Set up PostgreSQL database with PostGIS extension
  - Set up Redis for geospatial indexing
  - Configure development environment (virtual environment, dependencies)
  - Create database schema for users, emergency_contacts, incident_reports, sos_events, route_risk_cache, trust_score_events
  - Implement database connection pooling and migrations
  - Set up JWT authentication and device fingerprinting
  - _Requirements: 13.1, 13.4, 13.6_

- [ ] 2. Implement location telemetry and crowd density tracking
  - [x] 2.1 Create telemetry service for location ping ingestion
    - Implement POST /api/v1/telemetry/ping endpoint
    - Validate location data (latitude, longitude, accuracy)
    - Store location pings in Redis with GEOADD command
    - Set 60-second TTL on location pings
    - Implement rate limiting (100 requests/minute per device)
    - _Requirements: 2.1, 2.2, 2.8_
  
  - [x] 2.2 Write property test for location ping TTL
    - **Property 6: Location Ping TTL**
    - **Validates: Requirements 2.2, 9.4**
  
  - [ ] 2.3 Implement crowd density aggregation service
    - Create background task to aggregate pings every 10 seconds
    - Group location pings into 100-meter radius zones
    - Merge zones with fewer than 5 devices
    - Store aggregated data in Redis with 120-second TTL
    - Implement anonymization for device identifiers
    - _Requirements: 2.3, 9.1, 9.3, 9.5_
  
  - [ ] 2.4 Write property tests for crowd density aggregation
    - **Property 7: Zone-Based Aggregation**
    - **Property 39: Minimum Zone Size Enforcement**
    - **Property 40: Location Ping Anonymization**
    - **Property 41: Small Zone Merging**
    - **Validates: Requirements 2.3, 9.1, 9.3, 9.5**
  
  - [ ] 2.5 Create WebSocket endpoint for real-time heatmap updates
    - Implement WebSocket connection management
    - Push aggregated crowd density data to connected clients
    - Handle client disconnections gracefully
    - _Requirements: 2.4, 9.2_
  
  - [ ] 2.6 Write property test for privacy-preserving display
    - **Property 8: Privacy-Preserving Display**
    - **Validates: Requirements 2.4, 9.2**

- [ ] 3. Checkpoint - Verify telemetry system
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement route safety analysis system
  - [ ] 4.1 Create route analyzer service
    - Implement POST /api/v1/routes/analyze endpoint
    - Integrate Google Maps Directions API for route retrieval
    - Implement route hashing for cache keys
    - Store route analysis results in PostgreSQL and Redis cache (1-hour TTL)
    - _Requirements: 1.1, 8.2_
  
  - [ ] 4.2 Implement crime score calculation
    - Query Government_System API for crime data within 1km radius
    - Implement inverse distance weighting algorithm
    - Handle API failures with cached data fallback
    - Implement retry logic (3 attempts with exponential backoff)
    - Cache crime data for 24 hours
    - _Requirements: 1.7, 12.1, 12.3, 12.5, 12.6, 12.7_
  
  - [ ] 4.3 Write property tests for crime score calculation
    - **Property 4: Inverse Distance Weighting for Crime**
    - **Property 50: Crime Data Query Radius**
    - **Property 52: Government System Fallback**
    - **Property 56: Government System Retry Logic**
    - **Validates: Requirements 1.7, 12.1, 12.3, 12.7**
  
  - [ ] 4.4 Implement crowd score calculation
    - Query Redis for devices within 100m of route segments
    - Normalize density (0 devices = 0, 20+ devices = 100)
    - Calculate weighted average across route segments
    - _Requirements: 1.8_
  
  - [ ] 4.5 Implement commercial score calculation
    - Integrate Google Places API for nearby businesses
    - Query open establishments within 200m of route segments
    - Normalize score (0 places = 0, 10+ places = 100)
    - Calculate weighted average across route segments
    - _Requirements: 1.9, 8.5_
  
  - [ ] 4.6 Write property test for Google Places integration
    - **Property 38: Google Places Query for Commercial Activity**
    - **Validates: Requirements 8.5**
  
  - [ ] 4.7 Implement lighting score calculation
    - Integrate Google Street View Static API
    - Fetch images for route segments
    - Use OpenCV to analyze brightness (mean grayscale value)
    - Normalize to 0-100 scale
    - Calculate weighted average across route segments
    - _Requirements: 1.10, 8.4_
  
  - [ ] 4.8 Write property test for Street View integration
    - **Property 37: Street View Image Fetching**
    - **Validates: Requirements 8.4**
  
  - [ ] 4.9 Implement weighted safety score calculation
    - Combine factor scores with weights (crime: 40%, crowd: 30%, commercial: 20%, lighting: 10%)
    - Classify routes (SAFE > 70, MEDIUM 40-70, HIGH_RISK < 40)
    - Generate alternative routes for HIGH_RISK classifications
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [ ] 4.10 Write property tests for safety score calculation
    - **Property 1: Safety Score Range Invariant**
    - **Property 2: Safety Score Weighted Calculation**
    - **Property 3: High-Risk Routes Provide Alternatives**
    - **Validates: Requirements 1.1, 1.2, 1.6**
  
  - [ ] 4.11 Write unit tests for route analysis edge cases
    - Test classification boundaries (scores 39, 40, 70, 71)
    - Test empty route handling
    - Test API failure scenarios
    - _Requirements: 1.3, 1.4, 1.5_

- [ ] 5. Checkpoint - Verify route analysis system
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement SOS emergency system
  - [ ] 6.1 Create SOS service for activation and deactivation
    - Implement POST /api/v1/sos/activate endpoint
    - Create geofence with 50-meter radius in Redis
    - Send push notifications to devices within geofence
    - Send SMS/push alerts to emergency contacts with location and timestamp
    - Start location tracking (5-second intervals)
    - Store SOS event in PostgreSQL
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.7_
  
  - [ ] 6.2 Write property tests for SOS activation
    - **Property 10: SOS Activation Performance**
    - **Property 11: Emergency Contact Alert Delivery**
    - **Property 12: Geofence Notification Delivery**
    - **Property 13: Geofence Radius Invariant**
    - **Property 16: SOS Alert Content Completeness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.7**
  
  - [ ] 6.3 Implement SOS deactivation
    - Implement POST /api/v1/sos/deactivate endpoint
    - Stop sending alerts
    - Remove geofence from Redis
    - Update SOS event with deactivation details
    - Apply trust score adjustment based on deactivation reason
    - _Requirements: 3.6_
  
  - [ ] 6.4 Write property test for SOS deactivation cleanup
    - **Property 15: SOS Deactivation Cleanup**
    - **Validates: Requirements 3.6**
  
  - [ ] 6.5 Create radar interface backend
    - Implement GET /api/v1/sos/radar endpoint
    - Query nearby devices using Redis GEORADIUS (50m)
    - Calculate relative distance and bearing for each device
    - Anonymize device identifiers
    - Return device positions with 5-second refresh rate
    - _Requirements: 4.1, 4.2, 4.6, 4.7_
  
  - [ ] 6.6 Write property tests for radar interface
    - **Property 17: Radar Device Discovery**
    - **Property 18: Radar Coordinate Transformation**
    - **Property 21: Radar Refresh Rate**
    - **Property 22: Radar Anonymization**
    - **Validates: Requirements 4.1, 4.2, 4.6, 4.7**
  
  - [ ] 6.7 Implement real-time radar updates
    - Create background task to detect device entry/exit from geofence
    - Push updates to radar interface within 5 seconds
    - Handle WebSocket connections for real-time updates
    - _Requirements: 4.3, 4.4_
  
  - [ ] 6.8 Write property tests for radar real-time updates
    - **Property 19: Radar Device Entry Detection**
    - **Property 20: Radar Device Exit Detection**
    - **Validates: Requirements 4.3, 4.4**

- [ ] 7. Implement live video streaming for evidence
  - [ ] 7.1 Create video streaming service
    - Implement video upload endpoint for streaming chunks
    - Store video in secure cloud storage (AWS S3 or similar)
    - Generate stream URL for emergency contacts
    - Send stream URL to emergency contacts when streaming starts
    - _Requirements: 7.2, 7.3_
  
  - [ ] 7.2 Write property tests for video streaming
    - **Property 30: Video Stream Upload**
    - **Property 31: Video Stream URL Notification**
    - **Validates: Requirements 7.2, 7.3**
  
  - [ ] 7.3 Implement video buffering for poor connectivity
    - Buffer video chunks locally on mobile client
    - Upload buffered chunks when connectivity improves
    - Handle upload failures with retry logic
    - _Requirements: 7.6_
  
  - [ ] 7.4 Write property test for video buffering
    - **Property 33: Video Buffering and Delayed Upload**
    - **Validates: Requirements 7.6**
  
  - [ ] 7.5 Implement video recording completion
    - Stop streaming on SOS deactivation
    - Save complete recording to cloud storage
    - Attach video URL as evidence to incident report
    - _Requirements: 7.5, 7.7_
  
  - [ ] 7.6 Write property tests for video completion
    - **Property 32: Video Stream Termination and Persistence**
    - **Property 34: Video Evidence Attachment**
    - **Validates: Requirements 7.5, 7.7**

- [ ] 8. Checkpoint - Verify SOS and video systems
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement trust score management system
  - [ ] 9.1 Create trust score manager service
    - Implement trust score update function with adjustment rules
    - Apply score adjustments: reported (-10), assisted (+5), false_alarm (-15)
    - Clamp trust score to 0-100 range
    - Classify users based on score (Fraud: 0, Suspected: 1-30, Normal: 31-100)
    - Log all trust score events to trust_score_events table
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [ ] 9.2 Write property tests for trust score management
    - **Property 23: Trust Score Adjustment Correctness**
    - **Property 24: Trust Score Bounds Invariant**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.8**
  
  - [ ] 9.3 Implement fraud detection and account flagging
    - Flag accounts when trust score reaches 0
    - Detect multiple reports pattern (3+ in 30 days)
    - Detect false alarm pattern (2+ in 30 days)
    - Trigger account review for fraud classification
    - _Requirements: 5.9_
  
  - [ ] 9.4 Write property test for fraud classification
    - **Property 25: Fraud Classification Trigger**
    - **Validates: Requirements 5.9**
  
  - [ ] 9.5 Write unit tests for trust score edge cases
    - Test score boundaries (0, 1, 30, 31, 100)
    - Test classification transitions
    - Test multiple adjustment scenarios
    - _Requirements: 5.5, 5.6, 5.7_

- [ ] 10. Implement incident reporting system
  - [ ] 10.1 Create incident reporting service
    - Implement POST /api/v1/report/suspect endpoint
    - Create incident report with timestamp, geolocation, reporter_id, suspect_device_id
    - Support incident types: SOS_Trigger, Harassment, Poor_Lighting
    - Store evidence URLs (images/video) with report
    - Update suspect user's trust score
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6_
  
  - [ ] 10.2 Write property tests for incident reporting
    - **Property 26: Incident Report Creation Completeness**
    - **Property 27: Evidence Attachment**
    - **Property 29: Incident Type Validation**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**
  
  - [ ] 10.3 Implement Government System integration
    - Send incident reports to Government_System API endpoints
    - Include authentication credentials
    - Handle API failures with retry logic
    - Store government system reference ID
    - Submit reports within 30 seconds
    - _Requirements: 6.5, 12.2, 12.4_
  
  - [ ] 10.4 Write property tests for government integration
    - **Property 28: Government System Integration**
    - **Property 51: Incident Report Submission Latency**
    - **Property 53: Government System Authentication**
    - **Validates: Requirements 6.5, 12.2, 12.4**

- [ ] 11. Implement user profile and emergency contact management
  - [ ] 11.1 Create user profile service
    - Implement GET /api/v1/user/profile endpoint
    - Display trust score and classification
    - Calculate and display statistics (SOS count, assists, reports)
    - Assign safety badge based on trust score (Bronze: 30-50, Silver: 51-75, Gold: 76-100)
    - Update profile display within 10 seconds of trust score changes
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  
  - [ ] 11.2 Write property tests for profile statistics
    - **Property 44: Profile Statistics Accuracy**
    - **Property 45: Profile Update Latency**
    - **Validates: Requirements 10.3, 10.4, 10.5, 10.7**
  
  - [ ] 11.3 Create emergency contact management service
    - Implement endpoints for adding, updating, removing emergency contacts
    - Enforce maximum of 5 contacts per user
    - Require phone number, allow optional name
    - Save changes immediately to database
    - Ensure removed contacts don't receive future SOS alerts
    - _Requirements: 11.2, 11.3, 11.4, 11.6, 11.7_
  
  - [ ] 11.4 Write property tests for emergency contact management
    - **Property 46: Emergency Contact Capacity Limit**
    - **Property 47: Emergency Contact Required Fields**
    - **Property 48: Emergency Contact Persistence**
    - **Property 49: Emergency Contact Deletion**
    - **Validates: Requirements 11.2, 11.3, 11.4, 11.6, 11.7**
  
  - [ ] 11.5 Write unit test for first-time user setup
    - Test initial trust score assignment (50)
    - Test emergency contact prompt on first launch
    - _Requirements: 5.1, 11.1_

- [ ] 12. Implement device fingerprinting and authentication
  - [ ] 12.1 Create device fingerprinting service
    - Generate unique device fingerprint on installation
    - Store fingerprint separately from PII
    - Use fingerprint consistently across all device identification
    - Regenerate fingerprint on reinstallation
    - _Requirements: 13.1, 13.4, 13.5_
  
  - [ ] 12.2 Write property tests for device fingerprinting
    - **Property 57: Device Fingerprint Uniqueness**
    - **Property 58: Device Fingerprint Consistent Usage**
    - **Property 59: Device Fingerprint Data Separation**
    - **Property 60: Device Fingerprint Regeneration on Reinstall**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**
  
  - [ ] 12.3 Implement dual authentication
    - Require both user credentials and device fingerprint for API requests
    - Implement JWT token generation with device fingerprint claim
    - Validate both credentials on protected endpoints
    - Restrict access for fraud-classified devices
    - _Requirements: 13.6, 13.7_
  
  - [ ] 12.4 Write property tests for authentication
    - **Property 61: Dual Authentication Requirement**
    - **Property 62: Fraud Device Access Restriction**
    - **Validates: Requirements 13.6, 13.7**

- [ ] 13. Implement offline functionality and data synchronization
  - [ ] 13.1 Create offline queue management
    - Queue location pings locally when offline
    - Queue incident reports when offline
    - Implement exponential backoff for retries
    - Synchronize queued data within 30 seconds of reconnection
    - _Requirements: 15.2, 15.7_
  
  - [ ] 13.2 Write property tests for offline queuing
    - **Property 67: Offline Location Ping Queuing**
    - **Property 72: Data Synchronization on Reconnection**
    - **Validates: Requirements 15.2, 15.7**
  
  - [ ] 13.3 Implement offline SOS activation
    - Allow SOS activation using cached data when offline
    - Fall back to SMS alerts for emergency contacts
    - Queue SOS event for server sync when online
    - _Requirements: 15.1, 15.5_
  
  - [ ] 13.4 Write property tests for offline SOS
    - **Property 66: Offline SOS Activation**
    - **Property 70: Offline SMS Fallback**
    - **Validates: Requirements 15.1, 15.5**
  
  - [ ] 13.5 Implement offline data display
    - Display cached crowd density with staleness indicator
    - Allow viewing cached route safety scores
    - Cache map tiles for offline viewing
    - _Requirements: 15.3, 15.4, 15.6_
  
  - [ ] 13.6 Write property tests for offline display
    - **Property 68: Stale Data Indication**
    - **Property 69: Offline Route Cache Access**
    - **Property 71: Map Tile Caching**
    - **Validates: Requirements 15.3, 15.4, 15.6**

- [ ] 14. Checkpoint - Verify offline functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Implement mobile client UI with Flet
  - [x] 15.1 Create SafeMap home screen
    - Display Google Maps with current location
    - Render crowd density heatmap overlay
    - Implement destination search interface
    - Display route options with safety scores
    - Handle route selection
    - _Requirements: 8.1, 8.3, 8.6, 8.7_
  
  - [x] 15.2 Create SOS radar screen
    - Implement circular radar interface
    - Display nearby devices with distance and bearing
    - Update device positions every 5 seconds
    - Allow device selection for reporting
    - Implement video recording controls
    - Add SOS deactivation button
    - _Requirements: 4.5_
  
  - [x] 15.3 Create user profile screen
    - Display trust score and classification
    - Show safety badge (Bronze/Silver/Gold)
    - Display statistics (SOS count, assists, reports)
    - Implement emergency contact management UI
    - _Requirements: 10.1, 10.2_
  
  - [x] 15.4 Implement background location service
    - Send location pings every 30-60 seconds
    - Handle online/offline queue management
    - Respect battery optimization settings
    - Stop pings when location sharing is disabled
    - _Requirements: 2.1, 2.8_
  
  - [x] 15.5 Write unit tests for mobile UI interactions
    - Test route selection flow
    - Test SOS activation flow
    - Test emergency contact management
    - Test offline mode indicators

- [ ] 16. Implement performance optimizations and monitoring
  - [ ] 16.1 Optimize database queries
    - Add indexes for frequently queried fields
    - Implement query result caching
    - Use database connection pooling
    - Optimize PostGIS spatial queries
    - _Requirements: 14.6_
  
  - [ ] 16.2 Implement request prioritization
    - Prioritize SOS requests over route analysis
    - Implement request queuing for high load
    - Use asynchronous processing for incident reports
    - _Requirements: 14.5, 14.7_
  
  - [ ] 16.3 Write property tests for performance requirements
    - **Property 63: Safety Score Calculation Performance**
    - **Property 64: Asynchronous Incident Report Processing**
    - **Property 65: SOS Request Prioritization**
    - **Validates: Requirements 14.2, 14.5, 14.7**
  
  - [ ] 16.4 Set up logging and monitoring
    - Implement structured logging with severity levels
    - Sanitize PII from logs
    - Set up error alerts (SOS failures, database errors, API failures)
    - Monitor response times and error rates
    - _Requirements: Error Handling section_

- [-] 17. Implement comprehensive error handling
  - [x] 17.1 Add client-side error handling
    - Handle network failures with retry logic
    - Handle GPS/location errors gracefully
    - Handle API errors with fallbacks
    - Validate user input with inline errors
    - _Requirements: Error Handling section_
  
  - [x] 17.2 Add server-side error handling
    - Handle database errors with retries
    - Handle Redis failures with database fallback
    - Handle external API errors with caching
    - Implement validation error responses
    - Handle resource exhaustion gracefully
    - _Requirements: Error Handling section_
  
  - [-] 17.3 Write unit tests for error scenarios
    - Test network failure handling
    - Test invalid input handling
    - Test API failure fallbacks
    - Test resource exhaustion scenarios

- [ ] 18. Final integration and end-to-end testing
  - [ ] 18.1 Integration testing
    - Test end-to-end route analysis flow
    - Test end-to-end SOS activation flow
    - Test location ping processing pipeline
    - Test incident reporting flow
    - Test trust score update flow
    - _Requirements: All requirements_
  
  - [ ] 18.2 Write integration tests
    - Test API → Service → Database → Cache flows
    - Test Mobile → API → External API integrations
    - Test real-time WebSocket updates
  
  - [ ] 18.3 Security testing
    - Test authentication bypass attempts
    - Test SQL injection vulnerabilities
    - Test API rate limiting
    - Verify location data anonymization
    - Verify PII is not leaked in logs
    - _Requirements: 9.1, 9.2, 9.3, 13.4_
  
  - [ ] 18.4 Performance testing
    - Load test with 10,000 location pings per second
    - Measure route analysis response time under load
    - Test SOS activation latency with concurrent activations
    - Benchmark geospatial queries
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 19. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests verify component interactions
- The implementation uses Python throughout (FastAPI backend, Flet mobile, Hypothesis for property testing)
