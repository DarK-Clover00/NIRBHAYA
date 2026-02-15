# UI Design Specification: NIRBHAYA Mobile App (Flet)

## Design Philosophy: Indian Tricolour Theme

NIRBHAYA's visual identity is rooted in the **Indian Tricolour**, symbolizing national pride, safety, and integrity. Every UI element follows this theme to create a cohesive, patriotic, and trustworthy user experience.

---

## Color System

### Primary Palette

```python
# Indian Tricolour Colors
SAFFRON = "#FF9933"      # Primary action, warnings, SOS
INDIA_GREEN = "#138808"  # Success, safe routes, trust indicators
WHITE = "#FFFFFF"        # Backgrounds, content areas
NAVY_BLUE = "#000080"    # Text, icons, borders (Ashoka Chakra color)

# Supporting Colors
LIGHT_SAFFRON = "#FFB366"  # Hover states, light warnings
DARK_GREEN = "#0D6006"     # Active states, emphasis
LIGHT_GRAY = "#F5F5F5"     # Secondary backgrounds
DARK_GRAY = "#333333"      # Secondary text
```

### Color Usage Matrix

| Element | Color | Usage |
|---------|-------|-------|
| **SOS Button** | Saffron | Emergency trigger, swipe-to-activate |
| **Safe Route Card** | Green border/icon | Routes with score > 70 |
| **High Risk Warning** | Saffron background | Routes with score < 40 |
| **App Bar** | Saffron gradient | Top navigation bar |
| **Success Messages** | Green | Confirmations, completed actions |
| **Primary Text** | Navy Blue | Headers, body text |
| **Icons** | Navy Blue | Default state icons |
| **Borders** | Navy Blue | Card outlines, dividers |
| **Backgrounds** | White | Main content areas |

---

## Typography

```python
# Font Configuration
FONT_FAMILY = "Roboto"  # Primary font (fallback: Open Sans)

# Font Sizes
FONT_SIZE_HEADER = 24
FONT_SIZE_SUBHEADER = 18
FONT_SIZE_BODY = 14
FONT_SIZE_CAPTION = 12
FONT_SIZE_SMALL = 10

# Font Weights
FONT_WEIGHT_BOLD = "700"
FONT_WEIGHT_REGULAR = "400"
FONT_WEIGHT_LIGHT = "300"
```

---

## Screen Designs

### 1. SafeMap Screen (Home)

**Layout:**
```
┌─────────────────────────────────────┐
│ [Saffron App Bar]                   │ ← Saffron gradient
│ NIRBHAYA                    [Menu]  │
├─────────────────────────────────────┤
│                                     │
│         [Google Map View]           │ ← Full-screen map
│                                     │
│  [Green Markers] = Safe Zones       │
│  [Saffron Markers] = Risk Zones     │
│                                     │
│         [Crowd Heatmap Overlay]     │ ← Translucent green gradient
│                                     │
├─────────────────────────────────────┤
│ [Search Bar - Navy Blue Border]     │ ← Destination search
│ "Where do you want to go?"          │
├─────────────────────────────────────┤
│ [Floating SOS Button - Saffron]     │ ← Bottom-right corner
│         🚨 SOS                       │
└─────────────────────────────────────┘
```

**Flet Code Structure:**
```python
import flet as ft

# Color constants
SAFFRON = "#FF9933"
INDIA_GREEN = "#138808"
NAVY_BLUE = "#000080"
WHITE = "#FFFFFF"

def SafeMapScreen():
    return ft.Column(
        controls=[
            # App Bar
            ft.Container(
                content=ft.Row([
                    ft.Text("NIRBHAYA", size=24, weight="bold", color=WHITE),
                    ft.IconButton(icon=ft.icons.MENU, icon_color=WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=SAFFRON,
                padding=15,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[SAFFRON, "#FFB366"]
                )
            ),
            
            # Map Container (placeholder - integrate Google Maps)
            ft.Container(
                content=ft.Text("Map View", color=NAVY_BLUE),
                expand=True,
                bgcolor="#E8F5E9"  # Light green for map area
            ),
            
            # Search Bar
            ft.Container(
                content=ft.TextField(
                    hint_text="Where do you want to go?",
                    border_color=NAVY_BLUE,
                    prefix_icon=ft.icons.SEARCH,
                    bgcolor=WHITE
                ),
                padding=10
            ),
            
            # Floating SOS Button
            ft.FloatingActionButton(
                content=ft.Row([
                    ft.Icon(ft.icons.WARNING, color=WHITE),
                    ft.Text("SOS", color=WHITE, weight="bold")
                ]),
                bgcolor=SAFFRON,
                on_click=lambda _: activate_sos()
            )
        ],
        spacing=0
    )
```

---

### 2. Route Selection Screen

**Layout:**
```
┌─────────────────────────────────────┐
│ [Saffron App Bar]                   │
│ ← Route Options                     │
├─────────────────────────────────────┤
│                                     │
│    [Map with 2 Route Polylines]     │
│    - Green Line = Safe Route        │
│    - Saffron Line = Risky Route     │
│                                     │
├─────────────────────────────────────┤
│ [Bottom Sheet - White Background]   │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [Green Border Card]             │ │
│ │ ✓ SAFEST ROUTE (Recommended)   │ │
│ │ Safety Score: 85/100            │ │
│ │ [Green Progress Bar]            │ │
│ │ • High crowd density            │ │
│ │ • 12 open shops                 │ │
│ │ • No crime reports              │ │
│ │ Duration: 18 min | 3.2 km       │ │
│ │ [SELECT - Green Button]         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [Saffron Border Card]           │ │
│ │ ⚠ FASTEST ROUTE (High Risk)    │ │
│ │ Safety Score: 32/100            │ │
│ │ [Saffron Progress Bar]          │ │
│ │ • Low crowd density             │ │
│ │ • 2 crime reports nearby        │ │
│ │ • Poorly lit area               │ │
│ │ Duration: 12 min | 2.8 km       │ │
│ │ [NOT RECOMMENDED - Gray Button] │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Flet Code:**
```python
def RouteCard(route_data, is_safe=True):
    border_color = INDIA_GREEN if is_safe else SAFFRON
    icon = ft.icons.CHECK_CIRCLE if is_safe else ft.icons.WARNING
    icon_color = INDIA_GREEN if is_safe else SAFFRON
    
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(icon, color=icon_color),
                ft.Text(
                    "SAFEST ROUTE" if is_safe else "FASTEST ROUTE",
                    size=18,
                    weight="bold",
                    color=NAVY_BLUE
                )
            ]),
            
            # Safety Score
            ft.Text(f"Safety Score: {route_data['score']}/100", size=14),
            ft.ProgressBar(
                value=route_data['score'] / 100,
                color=INDIA_GREEN if is_safe else SAFFRON,
                bgcolor="#E0E0E0"
            ),
            
            # Details
            ft.Column([
                ft.Text(f"• {detail}", size=12, color=NAVY_BLUE)
                for detail in route_data['details']
            ]),
            
            # Duration and Distance
            ft.Text(
                f"Duration: {route_data['duration']} | {route_data['distance']}",
                size=12,
                color=DARK_GRAY
            ),
            
            # Action Button
            ft.ElevatedButton(
                text="SELECT" if is_safe else "NOT RECOMMENDED",
                bgcolor=INDIA_GREEN if is_safe else "#CCCCCC",
                color=WHITE,
                on_click=lambda _: select_route(route_data)
            )
        ]),
        border=ft.border.all(2, border_color),
        border_radius=8,
        padding=15,
        bgcolor=WHITE,
        margin=10
    )
```

---

### 3. SOS Radar Screen

**Layout:**
```
┌─────────────────────────────────────┐
│ [Saffron App Bar - Pulsing]         │
│ 🚨 SOS MODE ACTIVE                  │
├─────────────────────────────────────┤
│                                     │
│    [Circular Radar Display]         │
│         Tricolour Gradient          │
│                                     │
│           [You - Center]            │
│              ●                      │
│                                     │
│         ●  ●     ●                  │ ← Nearby devices
│      ●        ●                     │
│         ●  ●                        │
│                                     │
│    [Distance Rings: 10m, 25m, 50m]  │
│                                     │
├─────────────────────────────────────┤
│ [White Card]                        │
│ 7 devices detected within 50m       │
│ Tap a device to report              │
│                                     │
│ [Record Evidence - Green Button]    │
│ [I'm Safe - Swipe to Deactivate]    │
└─────────────────────────────────────┘
```

**Flet Code:**
```python
def SOSRadarScreen():
    return ft.Column([
        # Pulsing SOS Header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.WARNING, color=WHITE, size=30),
                ft.Text("SOS MODE ACTIVE", size=24, weight="bold", color=WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=SAFFRON,
            padding=20,
            animate=ft.animation.Animation(1000, "easeInOut")  # Pulsing effect
        ),
        
        # Radar Canvas
        ft.Container(
            content=ft.Canvas(
                # Draw radar circles and device dots
                # Implement custom paint for radar visualization
            ),
            expand=True,
            bgcolor=WHITE
        ),
        
        # Info Card
        ft.Container(
            content=ft.Column([
                ft.Text("7 devices detected within 50m", size=16, color=NAVY_BLUE),
                ft.Text("Tap a device to report", size=12, color=DARK_GRAY),
                
                # Action Buttons
                ft.ElevatedButton(
                    text="📹 Record Evidence",
                    bgcolor=INDIA_GREEN,
                    color=WHITE,
                    on_click=lambda _: start_recording()
                ),
                
                # Deactivation Slider
                ft.Container(
                    content=ft.Text("← Swipe to Deactivate SOS", color=WHITE),
                    bgcolor=NAVY_BLUE,
                    padding=15,
                    border_radius=25,
                    # Implement swipe gesture
                )
            ]),
            bgcolor=WHITE,
            padding=15,
            border=ft.border.all(1, NAVY_BLUE)
        )
    ])
```

---

### 4. User Profile Screen

**Layout:**
```
┌─────────────────────────────────────┐
│ [Saffron App Bar]                   │
│ ← Profile                           │
├─────────────────────────────────────┤
│ [White Card]                        │
│                                     │
│     [Profile Picture]               │
│     User Name                       │
│     +91 XXXXX XXXXX                 │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Trust Score: 85/100             │ │
│ │ [Green Progress Bar]            │ │
│ │ Status: ✓ Normal                │ │
│ │ Badge: 🥇 Gold                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Statistics - Navy Blue Cards]      │
│ ┌──────┐ ┌──────┐ ┌──────┐         │
│ │  5   │ │  12  │ │  0   │         │
│ │ SOS  │ │Helps │ │Reports│        │
│ └──────┘ └──────┘ └──────┘         │
│                                     │
│ [Emergency Contacts Section]        │
│ ┌─────────────────────────────────┐ │
│ │ 👤 Contact 1: Mom               │ │
│ │    +91 XXXXX XXXXX              │ │
│ ├─────────────────────────────────┤ │
│ │ 👤 Contact 2: Dad               │ │
│ │    +91 XXXXX XXXXX              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [+ Add Contact - Green Button]      │
└─────────────────────────────────────┘
```

---

## Component Library

### Buttons

```python
# Primary Button (Saffron)
ft.ElevatedButton(
    text="Primary Action",
    bgcolor=SAFFRON,
    color=WHITE,
    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
)

# Success Button (Green)
ft.ElevatedButton(
    text="Confirm",
    bgcolor=INDIA_GREEN,
    color=WHITE,
    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
)

# Secondary Button (Navy Blue Outline)
ft.OutlinedButton(
    text="Secondary",
    style=ft.ButtonStyle(
        color=NAVY_BLUE,
        side=ft.BorderSide(2, NAVY_BLUE)
    )
)
```

### Cards

```python
# Standard Card
ft.Container(
    content=ft.Column([...]),
    bgcolor=WHITE,
    border=ft.border.all(1, NAVY_BLUE),
    border_radius=8,
    padding=15,
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=5,
        color="#00000020"
    )
)

# Warning Card (Saffron)
ft.Container(
    content=ft.Column([...]),
    bgcolor="#FFF3E0",  # Light saffron
    border=ft.border.all(2, SAFFRON),
    border_radius=8,
    padding=15
)

# Success Card (Green)
ft.Container(
    content=ft.Column([...]),
    bgcolor="#E8F5E9",  # Light green
    border=ft.border.all(2, INDIA_GREEN),
    border_radius=8,
    padding=15
)
```

### Progress Bars

```python
# Safety Score Bar (Green)
ft.ProgressBar(
    value=0.85,  # 85/100
    color=INDIA_GREEN,
    bgcolor="#E0E0E0",
    height=8,
    border_radius=4
)

# Risk Score Bar (Saffron)
ft.ProgressBar(
    value=0.32,  # 32/100
    color=SAFFRON,
    bgcolor="#E0E0E0",
    height=8,
    border_radius=4
)
```

---

## Animations and Interactions

### SOS Button Pulse Animation
```python
ft.Container(
    animate=ft.animation.Animation(1000, "easeInOut"),
    # Pulsing scale effect for SOS button
)
```

### Route Card Slide-In
```python
ft.Container(
    animate_position=ft.animation.Animation(300, "easeOut"),
    # Slide up from bottom
)
```

### Radar Sweep Animation
```python
# Rotating sweep line on radar
ft.Container(
    animate_rotation=ft.animation.Animation(2000, "linear"),
    # Continuous rotation
)
```

---

## Accessibility

- **High Contrast**: Navy Blue text on White backgrounds (WCAG AAA compliant)
- **Large Touch Targets**: Minimum 48x48 dp for all interactive elements
- **Screen Reader Support**: All icons have text labels
- **Color Blindness**: Icons supplement color coding (not color-only indicators)

---

## Responsive Design

- **Mobile First**: Optimized for 360x640 dp (minimum)
- **Tablet Support**: Adaptive layout for larger screens
- **Orientation**: Portrait primary, landscape supported for map view

---

## Implementation Priority

1. **Phase 1**: SafeMap Screen with basic map integration
2. **Phase 2**: Route Selection with safety score cards
3. **Phase 3**: SOS Radar with real-time device tracking
4. **Phase 4**: Profile and settings screens

---

This UI specification ensures a cohesive, patriotic, and user-friendly experience while maintaining the Indian Tricolour theme throughout the application.
