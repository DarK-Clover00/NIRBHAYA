"""
User Profile screen - Display trust score, statistics, and emergency contacts
"""
import flet as ft
from typing import Optional, Callable, List, Dict
from ..config import SAFFRON, INDIA_GREEN, NAVY_BLUE, WHITE, DARK_GRAY


class ProfileScreen:
    """
    User profile screen displaying trust score, classification, safety badge,
    statistics, and emergency contact management.
    
    Requirements: 10.1, 10.2
    """
    
    def __init__(
        self,
        on_add_contact: Optional[Callable] = None,
        on_edit_contact: Optional[Callable] = None,
        on_delete_contact: Optional[Callable] = None,
        on_back: Optional[Callable] = None
    ):
        """
        Initialize Profile screen
        
        Args:
            on_add_contact: Callback when adding emergency contact
            on_edit_contact: Callback when editing emergency contact
            on_delete_contact: Callback when deleting emergency contact
            on_back: Callback when back button is pressed
        """
        self.on_add_contact = on_add_contact
        self.on_edit_contact = on_edit_contact
        self.on_delete_contact = on_delete_contact
        self.on_back = on_back
        
        self.trust_score_text = None
        self.trust_score_bar = None
        self.classification_text = None
        self.badge_icon = None
        self.stats_container = None
        self.contacts_container = None
        
    def build(self) -> ft.Column:
        """Build the Profile screen UI"""
        
        return ft.Column(
            [
                # App Bar
                self._build_app_bar(),
                
                # Scrollable content
                ft.Container(
                    content=ft.Column(
                        [
                            # Profile Header
                            self._build_profile_header(),
                            
                            # Trust Score Card
                            self._build_trust_score_card(),
                            
                            # Statistics Cards
                            self._build_statistics_section(),
                            
                            # Emergency Contacts Section
                            self._build_emergency_contacts_section(),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=15,
                    ),
                    padding=15,
                    expand=True,
                )
            ],
            spacing=0,
            expand=True,
        )
    
    def _build_app_bar(self) -> ft.Container:
        """Build the app bar"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color=WHITE,
                        on_click=lambda _: self._handle_back()
                    ),
                    ft.Text(
                        "Profile",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=WHITE
                    ),
                ],
                spacing=10,
            ),
            bgcolor=SAFFRON,
            padding=15,
        )
    
    def _build_profile_header(self) -> ft.Container:
        """Build profile header with user info"""
        return ft.Container(
            content=ft.Column(
                [
                    # Profile picture placeholder
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.ACCOUNT_CIRCLE,
                            size=80,
                            color=NAVY_BLUE
                        ),
                        alignment=ft.alignment.center,
                    ),
                    
                    # User name
                    ft.Text(
                        "User Name",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=NAVY_BLUE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    # Phone number
                    ft.Text(
                        "+91 XXXXX XXXXX",
                        size=14,
                        color=DARK_GRAY,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=WHITE,
            padding=20,
            border_radius=8,
            border=ft.border.all(1, NAVY_BLUE),
        )
    
    def _build_trust_score_card(self) -> ft.Container:
        """Build trust score display card"""
        # Initialize with default values
        self.trust_score_text = ft.Text(
            "Trust Score: 50/100",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=NAVY_BLUE
        )
        
        self.trust_score_bar = ft.ProgressBar(
            value=0.5,
            color=INDIA_GREEN,
            bgcolor="#E0E0E0",
            height=12,
        )
        
        self.classification_text = ft.Text(
            "Status: ✓ Normal",
            size=14,
            color=INDIA_GREEN,
            weight=ft.FontWeight.BOLD
        )
        
        self.badge_icon = ft.Row(
            [
                ft.Icon(ft.icons.MILITARY_TECH, color="#CD7F32", size=30),  # Bronze
                ft.Text(
                    "Bronze Badge",
                    size=16,
                    color=NAVY_BLUE,
                    weight=ft.FontWeight.BOLD
                )
            ],
            spacing=10,
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    self.trust_score_text,
                    self.trust_score_bar,
                    ft.Container(height=10),
                    self.classification_text,
                    ft.Container(height=10),
                    self.badge_icon,
                ],
                spacing=5,
            ),
            bgcolor=WHITE,
            padding=20,
            border_radius=8,
            border=ft.border.all(2, INDIA_GREEN),
        )
    
    def _build_statistics_section(self) -> ft.Container:
        """Build statistics cards section"""
        self.stats_container = ft.Row(
            [
                self._build_stat_card("SOS", "0", ft.icons.WARNING),
                self._build_stat_card("Helps", "0", ft.icons.VOLUNTEER_ACTIVISM),
                self._build_stat_card("Reports", "0", ft.icons.REPORT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Statistics",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=NAVY_BLUE
                    ),
                    self.stats_container,
                ],
                spacing=10,
            ),
        )
    
    def _build_stat_card(self, label: str, value: str, icon) -> ft.Container:
        """Build individual statistic card"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, color=NAVY_BLUE, size=30),
                    ft.Text(
                        value,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=NAVY_BLUE
                    ),
                    ft.Text(
                        label,
                        size=12,
                        color=DARK_GRAY
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=WHITE,
            padding=15,
            border_radius=8,
            border=ft.border.all(1, NAVY_BLUE),
            width=100,
        )
    
    def _build_emergency_contacts_section(self) -> ft.Container:
        """Build emergency contacts section"""
        self.contacts_container = ft.Column(
            [
                ft.Text(
                    "No emergency contacts added",
                    size=14,
                    color=DARK_GRAY,
                    italic=True
                )
            ],
            spacing=10,
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Emergency Contacts",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=NAVY_BLUE
                            ),
                            ft.Text(
                                "(Max 5)",
                                size=12,
                                color=DARK_GRAY
                            ),
                        ],
                        spacing=10,
                    ),
                    
                    self.contacts_container,
                    
                    # Add Contact Button
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.ADD, color=WHITE, size=20),
                                ft.Text("Add Contact", color=WHITE, size=14)
                            ],
                            spacing=5,
                        ),
                        bgcolor=INDIA_GREEN,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _: self._handle_add_contact(),
                    ),
                ],
                spacing=10,
            ),
        )
    
    def update_profile_data(self, profile_data: Dict):
        """
        Update profile display with user data
        
        Args:
            profile_data: Dictionary containing user profile information
        """
        # Update trust score
        trust_score = profile_data.get('trust_score', 50)
        self.trust_score_text.value = f"Trust Score: {trust_score}/100"
        self.trust_score_bar.value = trust_score / 100
        
        # Update classification
        classification = profile_data.get('classification', 'Normal')
        status_icon = "✓" if classification == "Normal" else "⚠"
        status_color = INDIA_GREEN if classification == "Normal" else SAFFRON
        self.classification_text.value = f"Status: {status_icon} {classification}"
        self.classification_text.color = status_color
        
        # Update badge
        badge = profile_data.get('safety_badge', 'Bronze')
        badge_colors = {
            'Gold': "#FFD700",
            'Silver': "#C0C0C0",
            'Bronze': "#CD7F32"
        }
        badge_color = badge_colors.get(badge, "#CD7F32")
        self.badge_icon.controls[0].color = badge_color
        self.badge_icon.controls[1].value = f"{badge} Badge"
        
        # Update statistics
        stats = profile_data.get('statistics', {})
        self._update_statistics(stats)
        
        # Update emergency contacts
        contacts = profile_data.get('emergency_contacts', [])
        self._update_contacts(contacts)
        
        # Note: update() should only be called when controls are added to page
    
    def _update_statistics(self, stats: Dict):
        """Update statistics display"""
        sos_count = stats.get('sos_activations', 0)
        assists = stats.get('assists_provided', 0)
        reports = stats.get('reports_filed_against', 0)
        
        # Update stat cards
        self.stats_container.controls[0].content.controls[1].value = str(sos_count)
        self.stats_container.controls[1].content.controls[1].value = str(assists)
        self.stats_container.controls[2].content.controls[1].value = str(reports)
        # Note: update() should only be called when control is added to page
    
    def _update_contacts(self, contacts: List[Dict]):
        """Update emergency contacts display"""
        if not contacts:
            self.contacts_container.controls = [
                ft.Text(
                    "No emergency contacts added",
                    size=14,
                    color=DARK_GRAY,
                    italic=True
                )
            ]
        else:
            self.contacts_container.controls = [
                self._build_contact_card(contact)
                for contact in contacts
            ]
        # Note: update() should only be called when control is added to page
    
    def _build_contact_card(self, contact: Dict) -> ft.Container:
        """Build emergency contact card"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.PERSON, color=NAVY_BLUE, size=30),
                    ft.Column(
                        [
                            ft.Text(
                                contact.get('name', 'Contact'),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=NAVY_BLUE
                            ),
                            ft.Text(
                                contact.get('phone', ''),
                                size=12,
                                color=DARK_GRAY
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color=NAVY_BLUE,
                        on_click=lambda _: self._handle_edit_contact(contact)
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=SAFFRON,
                        on_click=lambda _: self._handle_delete_contact(contact)
                    ),
                ],
                spacing=10,
            ),
            bgcolor=WHITE,
            padding=10,
            border_radius=8,
            border=ft.border.all(1, NAVY_BLUE),
        )
    
    def _handle_back(self):
        """Handle back button"""
        if self.on_back:
            self.on_back()
    
    def _handle_add_contact(self):
        """Handle add contact button"""
        if self.on_add_contact:
            self.on_add_contact()
    
    def _handle_edit_contact(self, contact: Dict):
        """Handle edit contact"""
        if self.on_edit_contact:
            self.on_edit_contact(contact)
    
    def _handle_delete_contact(self, contact: Dict):
        """Handle delete contact"""
        if self.on_delete_contact:
            self.on_delete_contact(contact)
