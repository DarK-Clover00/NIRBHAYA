"""
Main entry point for NIRBHAYA mobile application
"""
import flet as ft
from mobile.screens import SafeMapScreen, SOSRadarScreen, ProfileScreen
from mobile.screens.safe_map import create_floating_sos_button
from mobile.services import LocationService, OfflineQueue


class NirbhayaApp:
    """Main application controller"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_screen = None
        self.location_service = None
        self.offline_queue = None
        
        # Initialize services
        self._init_services()
        
        # Configure page
        self._configure_page()
        
        # Show home screen
        self.show_safe_map()
    
    def _init_services(self):
        """Initialize background services"""
        # TODO: Get actual device ID
        device_id = "test_device_001"
        
        self.location_service = LocationService(
            device_id=device_id,
            on_ping_success=self._on_ping_success,
            on_ping_failure=self._on_ping_failure
        )
        
        self.offline_queue = OfflineQueue(
            on_sync_complete=self._on_sync_complete
        )
    
    def _configure_page(self):
        """Configure page settings"""
        self.page.title = "NIRBHAYA - Women's Safety"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.spacing = 0
    
    def show_safe_map(self):
        """Show SafeMap home screen"""
        self.current_screen = SafeMapScreen(
            on_sos_activate=self.activate_sos,
            on_destination_search=self.search_destination,
            on_menu_click=self.show_menu
        )
        
        # Build screen
        screen_ui = self.current_screen.build()
        
        # Add floating SOS button
        self.page.controls = [
            ft.Stack(
                [
                    screen_ui,
                    ft.Container(
                        content=create_floating_sos_button(
                            on_click=lambda _: self.activate_sos()
                        ),
                        alignment=ft.alignment.bottom_right,
                        padding=20,
                    )
                ],
                expand=True,
            )
        ]
        self.page.update()
    
    def show_sos_radar(self):
        """Show SOS Radar screen"""
        self.current_screen = SOSRadarScreen(
            on_deactivate=self.deactivate_sos,
            on_device_report=self.report_device,
            on_start_recording=self.toggle_recording
        )
        
        self.page.controls = [self.current_screen.build()]
        self.page.update()
    
    def show_profile(self):
        """Show Profile screen"""
        self.current_screen = ProfileScreen(
            on_add_contact=self.add_emergency_contact,
            on_edit_contact=self.edit_emergency_contact,
            on_delete_contact=self.delete_emergency_contact,
            on_back=self.show_safe_map
        )
        
        self.page.controls = [self.current_screen.build()]
        self.page.update()
        
        # Load profile data
        # TODO: Fetch from backend
        profile_data = {
            "trust_score": 75,
            "classification": "Normal",
            "safety_badge": "Silver",
            "statistics": {
                "sos_activations": 2,
                "assists_provided": 5,
                "reports_filed_against": 0
            },
            "emergency_contacts": []
        }
        self.current_screen.update_profile_data(profile_data)
    
    def show_menu(self):
        """Show menu options"""
        # TODO: Implement menu
        self.show_profile()
    
    def activate_sos(self):
        """Activate SOS mode"""
        # TODO: Send SOS activation to backend
        self.show_sos_radar()
    
    def deactivate_sos(self):
        """Deactivate SOS mode"""
        # TODO: Send SOS deactivation to backend
        self.show_safe_map()
    
    def search_destination(self, destination: str):
        """Search for destination and show routes"""
        # TODO: Call backend API for route analysis
        # Mock data for now
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
            }
        ]
        
        if isinstance(self.current_screen, SafeMapScreen):
            self.current_screen.show_routes(routes)
    
    def report_device(self, device_id: str):
        """Report a suspicious device"""
        # TODO: Send incident report to backend
        pass
    
    def toggle_recording(self, is_recording: bool):
        """Toggle video recording"""
        # TODO: Implement video recording
        pass
    
    def add_emergency_contact(self):
        """Add emergency contact"""
        # TODO: Show dialog to add contact
        pass
    
    def edit_emergency_contact(self, contact: dict):
        """Edit emergency contact"""
        # TODO: Show dialog to edit contact
        pass
    
    def delete_emergency_contact(self, contact: dict):
        """Delete emergency contact"""
        # TODO: Confirm and delete contact
        pass
    
    def _on_ping_success(self, ping_data: dict):
        """Handle successful location ping"""
        pass
    
    def _on_ping_failure(self, error: str):
        """Handle location ping failure"""
        # Queue for offline sync
        if self.offline_queue:
            self.offline_queue.queue_location_ping(ping_data={})
    
    def _on_sync_complete(self, results: dict):
        """Handle offline sync completion"""
        pass


def main(page: ft.Page):
    """
    Main application entry point
    
    Args:
        page: Flet page object
    """
    NirbhayaApp(page)


if __name__ == "__main__":
    ft.app(target=main)
