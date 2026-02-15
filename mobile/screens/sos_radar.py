"""
SOS Radar screen - Circular radar interface showing nearby devices during SOS mode
"""
import flet as ft
from typing import Optional, Callable, List, Dict
from ..config import SAFFRON, INDIA_GREEN, NAVY_BLUE, WHITE, LIGHT_SAFFRON


class SOSRadarScreen:
    """
    SOS Radar screen with circular radar display showing nearby devices.
    Updates device positions every 5 seconds.
    
    Requirements: 4.5
    """
    
    def __init__(
        self,
        on_deactivate: Optional[Callable] = None,
        on_device_report: Optional[Callable] = None,
        on_start_recording: Optional[Callable] = None
    ):
        """
        Initialize SOS Radar screen
        
        Args:
            on_deactivate: Callback when SOS is deactivated
            on_device_report: Callback when a device is reported
            on_start_recording: Callback when video recording starts
        """
        self.on_deactivate = on_deactivate
        self.on_device_report = on_device_report
        self.on_start_recording = on_start_recording
        self.radar_canvas = None
        self.device_count_text = None
        self.nearby_devices = []
        self.is_recording = False
        
    def build(self) -> ft.Column:
        """Build the SOS Radar screen UI"""
        
        # Device count text
        self.device_count_text = ft.Text(
            "0 devices detected within 50m",
            size=16,
            color=NAVY_BLUE,
            weight=ft.FontWeight.BOLD
        )
        
        # Radar canvas
        self.radar_canvas = ft.Container(
            content=ft.Stack(
                [
                    # Radar background with gradient
                    ft.Container(
                        gradient=ft.RadialGradient(
                            colors=[
                                "#FFE5CC",  # Light saffron center
                                WHITE,
                                "#E8F5E9",  # Light green edge
                            ],
                            center=ft.alignment.center,
                            radius=1.0,
                        ),
                        expand=True,
                    ),
                    # Radar placeholder (Canvas will be implemented later)
                    ft.Container(
                        content=ft.Text(
                            "Radar Visualization",
                            size=12,
                            color=NAVY_BLUE,
                            opacity=0.3
                        ),
                        alignment=ft.alignment.center,
                    ),
                    # Center marker (user position)
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.PERSON_PIN_CIRCLE,
                            color=SAFFRON,
                            size=40
                        ),
                        alignment=ft.alignment.center,
                    ),
                ]
            ),
            expand=True,
            border=ft.border.all(2, NAVY_BLUE),
            border_radius=200,  # Circular
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        
        return ft.Column(
            [
                # Pulsing SOS Header
                self._build_sos_header(),
                
                # Radar Display
                ft.Container(
                    content=self.radar_canvas,
                    padding=20,
                    expand=True,
                ),
                
                # Info and Controls Card
                self._build_controls_card(),
            ],
            spacing=0,
            expand=True,
        )
    
    def _build_sos_header(self) -> ft.Container:
        """Build the pulsing SOS header"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.WARNING, color=WHITE, size=30),
                    ft.Text(
                        "SOS MODE ACTIVE",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=WHITE
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=SAFFRON,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[SAFFRON, LIGHT_SAFFRON]
            ),
            # Pulsing animation
            animate=ft.animation.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        )
    
    def _build_controls_card(self) -> ft.Container:
        """Build the controls card with device info and action buttons"""
        return ft.Container(
            content=ft.Column(
                [
                    # Device count
                    self.device_count_text,
                    
                    ft.Text(
                        "Tap a device on radar to report",
                        size=12,
                        color="#666666"
                    ),
                    
                    ft.Divider(height=10, color=NAVY_BLUE),
                    
                    # Distance legend
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("10m", size=10, color=NAVY_BLUE),
                                width=50,
                            ),
                            ft.Container(
                                content=ft.Text("25m", size=10, color=NAVY_BLUE),
                                width=50,
                            ),
                            ft.Container(
                                content=ft.Text("50m", size=10, color=NAVY_BLUE),
                                width=50,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    
                    ft.Divider(height=10, color=NAVY_BLUE),
                    
                    # Action Buttons
                    ft.Row(
                        [
                            # Record Evidence Button
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            ft.icons.VIDEOCAM if not self.is_recording else ft.icons.STOP,
                                            color=WHITE,
                                            size=20
                                        ),
                                        ft.Text(
                                            "Record" if not self.is_recording else "Stop",
                                            color=WHITE,
                                            size=14
                                        )
                                    ],
                                    spacing=5,
                                ),
                                bgcolor=INDIA_GREEN if not self.is_recording else SAFFRON,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                on_click=lambda _: self._toggle_recording(),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    
                    # Deactivation Slider
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.SWIPE, color=WHITE, size=20),
                                ft.Text(
                                    "Swipe to Deactivate SOS",
                                    color=WHITE,
                                    size=14,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Icon(ft.icons.ARROW_FORWARD, color=WHITE, size=20),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        bgcolor=NAVY_BLUE,
                        padding=15,
                        border_radius=25,
                        on_click=lambda _: self._handle_deactivate(),
                        # TODO: Implement swipe gesture
                    ),
                ],
                spacing=10,
            ),
            bgcolor=WHITE,
            padding=15,
            border=ft.border.all(1, NAVY_BLUE),
            border_radius=8,
        )
    
    def update_nearby_devices(self, devices: List[Dict]):
        """
        Update the list of nearby devices and refresh radar display
        
        Args:
            devices: List of device dictionaries with distance and bearing
                    Format: [{"device_id": str, "distance": float, "bearing": float}]
        """
        self.nearby_devices = devices
        
        # Update device count
        count = len(devices)
        self.device_count_text.value = f"{count} device{'s' if count != 1 else ''} detected within 50m"
        # Note: update() should only be called when control is added to page
        
        # TODO: Redraw radar canvas with device positions
        self._draw_radar_devices()
    
    def _draw_radar_devices(self):
        """Draw device markers on radar based on distance and bearing"""
        # TODO: Implement custom canvas drawing for device positions
        # This would use the Canvas widget to draw:
        # - Concentric circles at 10m, 25m, 50m
        # - Device dots at calculated positions based on bearing and distance
        # - Sweep line animation
        pass
    
    def _toggle_recording(self):
        """Toggle video recording"""
        self.is_recording = not self.is_recording
        if self.on_start_recording:
            self.on_start_recording(self.is_recording)
    
    def _handle_deactivate(self):
        """Handle SOS deactivation"""
        if self.on_deactivate:
            self.on_deactivate()
    
    def _handle_device_tap(self, device_id: str):
        """Handle device selection for reporting"""
        if self.on_device_report:
            self.on_device_report(device_id)


def create_radar_canvas(devices: List[Dict], radius: float = 200):
    """
    Create radar canvas visualization
    
    Args:
        devices: List of nearby devices with distance and bearing
        radius: Radar display radius in pixels
    
    Returns:
        Canvas widget for radar visualization
    
    Note: This is a placeholder. Full canvas implementation requires
    custom paint methods which will be implemented when integrating
    with the actual Flet canvas API.
    """
    # TODO: Implement custom canvas drawing for radar
    # This would use ft.canvas module to draw:
    # - Concentric circles at 10m, 25m, 50m
    # - Device dots at calculated positions based on bearing and distance
    # - Sweep line animation
    
    # For now, return a placeholder container
    return ft.Container(
        content=ft.Text(
            "Radar Canvas Placeholder",
            size=12,
            color=NAVY_BLUE,
            opacity=0.5
        ),
        alignment=ft.alignment.center,
    )
