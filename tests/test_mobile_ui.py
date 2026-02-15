"""
Unit tests for mobile UI interactions
"""
import pytest
import asyncio
from mobile.screens.safe_map import SafeMapScreen, create_floating_sos_button
from mobile.screens.sos_radar import SOSRadarScreen
from mobile.screens.profile import ProfileScreen
from mobile.services.location_service import LocationService, BatteryOptimizer
from mobile.services.offline_queue import OfflineQueue


class TestSafeMapScreen:
    """Test SafeMap home screen functionality"""
    
    def test_safe_map_screen_initialization(self):
        """Test SafeMap screen can be initialized"""
        screen = SafeMapScreen()
        assert screen is not None
        assert screen.search_field is None
        assert screen.map_container is None
    
    def test_safe_map_screen_build(self):
        """Test SafeMap screen builds UI components"""
        screen = SafeMapScreen()
        ui = screen.build()
        
        assert ui is not None
        assert len(ui.controls) > 0
    
    def test_safe_map_callbacks(self):
        """Test SafeMap screen callbacks are invoked"""
        sos_called = False
        search_called = False
        menu_called = False
        
        def on_sos():
            nonlocal sos_called
            sos_called = True
        
        def on_search(dest):
            nonlocal search_called
            search_called = True
        
        def on_menu():
            nonlocal menu_called
            menu_called = True
        
        screen = SafeMapScreen(
            on_sos_activate=on_sos,
            on_destination_search=on_search,
            on_menu_click=on_menu
        )
        
        # Build UI to initialize components
        screen.build()
        
        # Test search callback
        screen.search_field.value = "Test Destination"
        screen._handle_search(None)
        assert search_called
        
        # Test menu callback
        screen._handle_menu_click()
        assert menu_called
    
    def test_show_routes(self):
        """Test route selection flow"""
        screen = SafeMapScreen()
        screen.build()
        
        # Test with empty routes
        screen.show_routes([])
        assert not screen.route_cards_container.visible
        
        # Test with routes
        routes = [
            {
                "safety_score": 85,
                "risk_classification": "SAFE",
                "factors": {
                    "crowd_score": 80,
                    "crime_score": 90,
                    "commercial_score": 75,
                    "lighting_score": 70
                },
                "duration": "15 min",
                "distance": "2.5 km"
            },
            {
                "safety_score": 35,
                "risk_classification": "HIGH_RISK",
                "factors": {
                    "crowd_score": 20,
                    "crime_score": 30,
                    "commercial_score": 40,
                    "lighting_score": 50
                },
                "duration": "10 min",
                "distance": "2.0 km"
            }
        ]
        
        screen.show_routes(routes)
        assert screen.route_cards_container.visible
        assert screen.route_cards_container.height == 300
    
    def test_floating_sos_button(self):
        """Test SOS button creation"""
        clicked = False
        
        def on_click(e):
            nonlocal clicked
            clicked = True
        
        button = create_floating_sos_button(on_click=on_click)
        assert button is not None
        assert button.bgcolor == "#FF9933"  # SAFFRON


class TestSOSRadarScreen:
    """Test SOS Radar screen functionality"""
    
    def test_sos_radar_initialization(self):
        """Test SOS Radar screen can be initialized"""
        screen = SOSRadarScreen()
        assert screen is not None
        assert screen.nearby_devices == []
        assert not screen.is_recording
    
    def test_sos_radar_build(self):
        """Test SOS Radar screen builds UI components"""
        screen = SOSRadarScreen()
        ui = screen.build()
        
        assert ui is not None
        assert len(ui.controls) > 0
    
    def test_update_nearby_devices(self):
        """Test updating nearby devices on radar"""
        screen = SOSRadarScreen()
        screen.build()
        
        devices = [
            {"device_id": "device1", "distance": 15.5, "bearing": 45},
            {"device_id": "device2", "distance": 30.2, "bearing": 180},
            {"device_id": "device3", "distance": 45.8, "bearing": 270}
        ]
        
        screen.update_nearby_devices(devices)
        
        assert len(screen.nearby_devices) == 3
        assert "3 devices detected within 50m" in screen.device_count_text.value
    
    def test_toggle_recording(self):
        """Test video recording toggle"""
        recording_states = []
        
        def on_recording(is_recording):
            recording_states.append(is_recording)
        
        screen = SOSRadarScreen(on_start_recording=on_recording)
        screen.build()
        
        # Start recording
        screen._toggle_recording()
        assert screen.is_recording
        assert recording_states[-1] is True
        
        # Stop recording
        screen._toggle_recording()
        assert not screen.is_recording
        assert recording_states[-1] is False
    
    def test_sos_deactivation(self):
        """Test SOS deactivation flow"""
        deactivated = False
        
        def on_deactivate():
            nonlocal deactivated
            deactivated = True
        
        screen = SOSRadarScreen(on_deactivate=on_deactivate)
        screen.build()
        
        screen._handle_deactivate()
        assert deactivated


class TestProfileScreen:
    """Test user profile screen functionality"""
    
    def test_profile_screen_initialization(self):
        """Test Profile screen can be initialized"""
        screen = ProfileScreen()
        assert screen is not None
    
    def test_profile_screen_build(self):
        """Test Profile screen builds UI components"""
        screen = ProfileScreen()
        ui = screen.build()
        
        assert ui is not None
        assert len(ui.controls) > 0
    
    def test_update_profile_data(self):
        """Test updating profile with user data"""
        screen = ProfileScreen()
        screen.build()
        
        profile_data = {
            "trust_score": 75,
            "classification": "Normal",
            "safety_badge": "Silver",
            "statistics": {
                "sos_activations": 3,
                "assists_provided": 8,
                "reports_filed_against": 0
            },
            "emergency_contacts": [
                {"name": "Mom", "phone": "+91 1234567890"},
                {"name": "Dad", "phone": "+91 0987654321"}
            ]
        }
        
        screen.update_profile_data(profile_data)
        
        assert "75/100" in screen.trust_score_text.value
        assert screen.trust_score_bar.value == 0.75
        assert "Normal" in screen.classification_text.value
        assert "Silver" in screen.badge_icon.controls[1].value
    
    def test_emergency_contact_management(self):
        """Test emergency contact management"""
        add_called = False
        edit_called = False
        delete_called = False
        
        def on_add():
            nonlocal add_called
            add_called = True
        
        def on_edit(contact):
            nonlocal edit_called
            edit_called = True
        
        def on_delete(contact):
            nonlocal delete_called
            delete_called = True
        
        screen = ProfileScreen(
            on_add_contact=on_add,
            on_edit_contact=on_edit,
            on_delete_contact=on_delete
        )
        screen.build()
        
        # Test add
        screen._handle_add_contact()
        assert add_called
        
        # Test edit
        contact = {"name": "Test", "phone": "+91 1234567890"}
        screen._handle_edit_contact(contact)
        assert edit_called
        
        # Test delete
        screen._handle_delete_contact(contact)
        assert delete_called
    
    def test_update_contacts_display(self):
        """Test updating emergency contacts display"""
        screen = ProfileScreen()
        screen.build()
        
        # Test with no contacts
        screen._update_contacts([])
        assert len(screen.contacts_container.controls) == 1
        assert "No emergency contacts" in screen.contacts_container.controls[0].value
        
        # Test with contacts
        contacts = [
            {"name": "Contact 1", "phone": "+91 1111111111"},
            {"name": "Contact 2", "phone": "+91 2222222222"}
        ]
        screen._update_contacts(contacts)
        assert len(screen.contacts_container.controls) == 2


class TestLocationService:
    """Test background location service"""
    
    @pytest.mark.asyncio
    async def test_location_service_initialization(self):
        """Test location service can be initialized"""
        service = LocationService(device_id="test_device")
        assert service is not None
        assert service.device_id == "test_device"
        assert not service.is_running
        assert service.is_enabled
    
    @pytest.mark.asyncio
    async def test_location_service_start_stop(self):
        """Test starting and stopping location service"""
        service = LocationService(device_id="test_device")
        
        # Start service
        await service.start()
        assert service.is_running
        
        # Stop service
        await service.stop()
        assert not service.is_running
    
    @pytest.mark.asyncio
    async def test_disable_location_sharing(self):
        """Test disabling location sharing stops pings immediately"""
        service = LocationService(device_id="test_device")
        
        # Enable and verify
        service.enable_location_sharing()
        assert service.is_enabled
        
        # Disable and verify
        service.disable_location_sharing()
        assert not service.is_enabled
    
    @pytest.mark.asyncio
    async def test_update_location(self):
        """Test updating current location"""
        service = LocationService(device_id="test_device")
        
        service.update_location(
            latitude=28.6139,
            longitude=77.2090,
            accuracy=10.5
        )
        
        assert service.current_location is not None
        assert service.current_location["latitude"] == 28.6139
        assert service.current_location["longitude"] == 77.2090
        assert service.current_location["accuracy"] == 10.5
    
    @pytest.mark.asyncio
    async def test_offline_queue_management(self):
        """Test queuing pings when offline"""
        service = LocationService(device_id="test_device")
        
        ping_data = {
            "device_id": "test_device",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "accuracy": 10.5
        }
        
        service._queue_ping(ping_data)
        assert service.get_queue_size() == 1
        
        # Test queue size limit
        for i in range(150):
            service._queue_ping(ping_data)
        
        assert service.get_queue_size() <= 100


class TestBatteryOptimizer:
    """Test battery optimization"""
    
    def test_battery_optimizer_initialization(self):
        """Test battery optimizer can be initialized"""
        optimizer = BatteryOptimizer()
        assert optimizer is not None
        assert optimizer.battery_level == 100
        assert not optimizer.is_charging
    
    def test_update_battery_status(self):
        """Test updating battery status"""
        optimizer = BatteryOptimizer()
        
        optimizer.update_battery_status(level=50, is_charging=True)
        assert optimizer.battery_level == 50
        assert optimizer.is_charging
    
    def test_recommended_interval_charging(self):
        """Test recommended interval when charging"""
        optimizer = BatteryOptimizer()
        optimizer.update_battery_status(level=30, is_charging=True)
        
        interval = optimizer.get_recommended_interval()
        assert interval == 30  # Minimum interval when charging
    
    def test_recommended_interval_low_battery(self):
        """Test recommended interval with low battery"""
        optimizer = BatteryOptimizer()
        optimizer.update_battery_status(level=15, is_charging=False)
        
        interval = optimizer.get_recommended_interval()
        assert interval == 60  # Maximum interval for low battery
    
    def test_should_reduce_frequency(self):
        """Test frequency reduction check"""
        optimizer = BatteryOptimizer()
        
        # High battery - no reduction
        optimizer.update_battery_status(level=80, is_charging=False)
        assert not optimizer.should_reduce_frequency()
        
        # Low battery - reduce
        optimizer.update_battery_status(level=15, is_charging=False)
        assert optimizer.should_reduce_frequency()
        
        # Low battery but charging - no reduction
        optimizer.update_battery_status(level=15, is_charging=True)
        assert not optimizer.should_reduce_frequency()


class TestOfflineQueue:
    """Test offline queue management"""
    
    def test_offline_queue_initialization(self):
        """Test offline queue can be initialized"""
        queue = OfflineQueue()
        assert queue is not None
        assert not queue.has_pending_data()
    
    def test_queue_location_ping(self):
        """Test queuing location pings"""
        queue = OfflineQueue()
        
        ping_data = {
            "device_id": "test_device",
            "latitude": 28.6139,
            "longitude": 77.2090
        }
        
        queue.queue_location_ping(ping_data)
        
        sizes = queue.get_queue_sizes()
        assert sizes["location_pings"] == 1
        assert queue.has_pending_data()
    
    def test_queue_incident_report(self):
        """Test queuing incident reports"""
        queue = OfflineQueue()
        
        report_data = {
            "reporter_id": "user123",
            "suspect_device_id": "device456",
            "incident_type": "SOS_Trigger"
        }
        
        queue.queue_incident_report(report_data)
        
        sizes = queue.get_queue_sizes()
        assert sizes["incident_reports"] == 1
    
    def test_queue_size_limit(self):
        """Test queue size limit enforcement"""
        queue = OfflineQueue(max_size=10)
        
        # Add more than max_size items
        for i in range(15):
            queue.queue_location_ping({"id": i})
        
        sizes = queue.get_queue_sizes()
        assert sizes["location_pings"] == 10  # Should be limited to max_size
    
    @pytest.mark.asyncio
    async def test_synchronize_queue(self):
        """Test synchronizing queued data"""
        queue = OfflineQueue()
        
        # Add some data
        queue.queue_location_ping({"id": 1})
        queue.queue_location_ping({"id": 2})
        
        sent_items = []
        
        async def mock_send(data_type, data):
            sent_items.append((data_type, data))
            return True
        
        results = await queue.synchronize(mock_send)
        
        assert results["location_pings"]["sent"] == 2
        assert results["location_pings"]["failed"] == 0
        assert len(sent_items) == 2
    
    def test_clear_all(self):
        """Test clearing all queues"""
        queue = OfflineQueue()
        
        queue.queue_location_ping({"id": 1})
        queue.queue_incident_report({"id": 2})
        
        assert queue.has_pending_data()
        
        queue.clear_all()
        
        assert not queue.has_pending_data()
        sizes = queue.get_queue_sizes()
        assert sizes["total"] == 0


class TestOfflineModeIndicators:
    """Test offline mode indicators"""
    
    def test_offline_queue_status(self):
        """Test offline mode indicators show queue status"""
        queue = OfflineQueue()
        
        # No pending data
        assert not queue.has_pending_data()
        
        # Add data
        queue.queue_location_ping({"id": 1})
        assert queue.has_pending_data()
        
        # Check sizes
        sizes = queue.get_queue_sizes()
        assert sizes["total"] == 1
