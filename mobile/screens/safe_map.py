"""
SafeMap home screen - Main map interface with crowd density and route analysis
"""
import flet as ft
from typing import Optional, Callable
from ..config import SAFFRON, INDIA_GREEN, NAVY_BLUE, WHITE, LIGHT_SAFFRON


class SafeMapScreen:
    """
    Main home screen displaying Google Maps with crowd density heatmap,
    destination search, and route safety analysis.
    
    Requirements: 8.1, 8.3, 8.6, 8.7
    """
    
    def __init__(
        self,
        on_sos_activate: Optional[Callable] = None,
        on_destination_search: Optional[Callable] = None,
        on_menu_click: Optional[Callable] = None
    ):
        """
        Initialize SafeMap screen
        
        Args:
            on_sos_activate: Callback when SOS button is pressed
            on_destination_search: Callback when destination is searched
            on_menu_click: Callback when menu is clicked
        """
        self.on_sos_activate = on_sos_activate
        self.on_destination_search = on_destination_search
        self.on_menu_click = on_menu_click
        self.search_field = None
        self.map_container = None
        self.route_cards_container = None
        
    def build(self) -> ft.Column:
        """Build the SafeMap screen UI"""
        
        # Search field for destination
        self.search_field = ft.TextField(
            hint_text="Where do you want to go?",
            border_color=NAVY_BLUE,
            prefix_icon=ft.icons.SEARCH,
            bgcolor=WHITE,
            on_submit=self._handle_search,
            text_size=14,
        )
        
        # Map container (placeholder for Google Maps integration)
        self.map_container = ft.Container(
            content=ft.Stack(
                [
                    # Map placeholder
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.icons.MAP,
                                    size=64,
                                    color=NAVY_BLUE,
                                    opacity=0.3
                                ),
                                ft.Text(
                                    "Map View",
                                    size=16,
                                    color=NAVY_BLUE,
                                    opacity=0.5
                                ),
                                ft.Text(
                                    "Google Maps integration pending",
                                    size=12,
                                    color=NAVY_BLUE,
                                    opacity=0.3
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor="#E8F5E9",  # Light green for map area
                        expand=True,
                    ),
                    # Current location marker
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.MY_LOCATION,
                            color=SAFFRON,
                            size=30
                        ),
                        alignment=ft.alignment.center,
                    ),
                ]
            ),
            expand=True,
        )
        
        # Route cards container (shown after search)
        self.route_cards_container = ft.Container(
            visible=False,
            height=0,
        )
        
        return ft.Column(
            controls=[
                # App Bar with tricolour gradient
                self._build_app_bar(),
                
                # Map view
                self.map_container,
                
                # Search bar
                ft.Container(
                    content=self.search_field,
                    padding=10,
                    bgcolor=WHITE,
                ),
                
                # Route cards (hidden initially)
                self.route_cards_container,
            ],
            spacing=0,
            expand=True,
        )
    
    def _build_app_bar(self) -> ft.Container:
        """Build the app bar with Indian tricolour theme"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "NIRBHAYA",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=WHITE
                    ),
                    ft.IconButton(
                        icon=ft.icons.MENU,
                        icon_color=WHITE,
                        on_click=lambda _: self._handle_menu_click()
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=SAFFRON,
            padding=15,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[SAFFRON, LIGHT_SAFFRON]
            )
        )
    
    def _handle_search(self, e):
        """Handle destination search"""
        if self.search_field and self.search_field.value:
            destination = self.search_field.value
            if self.on_destination_search:
                self.on_destination_search(destination)
    
    def _handle_menu_click(self):
        """Handle menu button click"""
        if self.on_menu_click:
            self.on_menu_click()
    
    def show_routes(self, routes: list):
        """
        Display route options with safety scores
        
        Args:
            routes: List of route dictionaries with safety scores
        """
        if not routes:
            return
        
        route_cards = []
        for route in routes:
            route_cards.append(self._build_route_card(route))
        
        self.route_cards_container.content = ft.Column(
            controls=route_cards,
            scroll=ft.ScrollMode.AUTO,
        )
        self.route_cards_container.visible = True
        self.route_cards_container.height = 300
        # Note: update() should only be called when control is added to page
    
    def _build_route_card(self, route: dict) -> ft.Container:
        """
        Build a route card with safety score
        
        Args:
            route: Route data including score, classification, factors
        """
        score = route.get('safety_score', 0)
        classification = route.get('risk_classification', 'MEDIUM')
        is_safe = classification == 'SAFE'
        
        border_color = INDIA_GREEN if is_safe else SAFFRON
        icon = ft.icons.CHECK_CIRCLE if is_safe else ft.icons.WARNING
        icon_color = INDIA_GREEN if is_safe else SAFFRON
        
        # Build factor details
        factors = route.get('factors', {})
        details = []
        if factors.get('crowd_score', 0) > 70:
            details.append("• High crowd density")
        elif factors.get('crowd_score', 0) < 40:
            details.append("• Low crowd density")
        
        if factors.get('crime_score', 0) > 70:
            details.append("• No recent crime reports")
        elif factors.get('crime_score', 0) < 40:
            details.append("• Crime reports nearby")
        
        if factors.get('commercial_score', 0) > 70:
            details.append("• Many open shops")
        elif factors.get('commercial_score', 0) < 40:
            details.append("• Few open establishments")
        
        if factors.get('lighting_score', 0) < 40:
            details.append("• Poorly lit area")
        
        return ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Row(
                        [
                            ft.Icon(icon, color=icon_color, size=24),
                            ft.Text(
                                "SAFEST ROUTE" if is_safe else "ALTERNATIVE ROUTE",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=NAVY_BLUE
                            )
                        ],
                        spacing=10,
                    ),
                    
                    # Safety Score
                    ft.Row(
                        [
                            ft.Text(
                                f"Safety Score: {score}/100",
                                size=14,
                                color=NAVY_BLUE
                            ),
                            ft.Text(
                                f"({classification})",
                                size=12,
                                color=icon_color,
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        spacing=10,
                    ),
                    
                    # Progress bar
                    ft.ProgressBar(
                        value=score / 100,
                        color=INDIA_GREEN if is_safe else SAFFRON,
                        bgcolor="#E0E0E0",
                        height=8,
                    ),
                    
                    # Details
                    ft.Column(
                        [
                            ft.Text(detail, size=12, color=NAVY_BLUE)
                            for detail in details
                        ],
                        spacing=2,
                    ),
                    
                    # Duration and Distance
                    ft.Text(
                        f"Duration: {route.get('duration', 'N/A')} | Distance: {route.get('distance', 'N/A')}",
                        size=12,
                        color="#666666"
                    ),
                    
                    # Action Button
                    ft.ElevatedButton(
                        text="SELECT ROUTE" if is_safe else "SELECT ANYWAY",
                        bgcolor=INDIA_GREEN if is_safe else "#CCCCCC",
                        color=WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _: self._select_route(route)
                    )
                ],
                spacing=8,
            ),
            border=ft.border.all(2, border_color),
            border_radius=8,
            padding=15,
            bgcolor=WHITE,
            margin=ft.margin.only(bottom=10),
        )
    
    def _select_route(self, route: dict):
        """Handle route selection"""
        # TODO: Implement route selection logic
        pass
    
    def update_crowd_heatmap(self, heatmap_data: dict):
        """
        Update crowd density heatmap overlay
        
        Args:
            heatmap_data: Crowd density zone data
        """
        # TODO: Implement heatmap overlay on map
        pass


def create_floating_sos_button(on_click: Optional[Callable] = None) -> ft.FloatingActionButton:
    """
    Create the floating SOS button
    
    Args:
        on_click: Callback when SOS button is pressed
    
    Returns:
        FloatingActionButton configured for SOS
    """
    return ft.FloatingActionButton(
        content=ft.Row(
            [
                ft.Icon(ft.icons.WARNING, color=WHITE, size=24),
                ft.Text("SOS", color=WHITE, weight=ft.FontWeight.BOLD, size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=SAFFRON,
        on_click=on_click,
        width=100,
        height=56,
    )
