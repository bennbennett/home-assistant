# Mobile Dashboard Implementation Plan

**Project Goal:** Create a standalone mobile dashboard (`mobile-redesign.yaml`) that implements React UI design while preserving all tablet dashboard functionality (6 rooms, scenes, tasks, calendar, devices, people management).

## Project Analysis Summary

### Tablet Dashboard Current State
- **6 Rooms:** Whole House, Living Room, Kitchen, Bedroom, Toby's Room, Outside
- **Navigation:** 80px side menu with 5 sections (Calendar, Tasks, Rooms, Devices, People)
- **Entities:** 15+ lights, 6+ temperature sensors, media players, vacuum, cameras
- **Features:** Scene controls, browser-mod popups, complex room cards, Toby's activity tracking
- **Templates:** Sophisticated button cards with status indicators and interactive controls

### Mobile UI Design Analysis
- **Technology:** React + Tailwind CSS design system
- **Layout:** Mobile container (max-width: 448px) with bottom navigation
- **Colors:** Light theme with semantic colors (blue primary, green/red/orange status)
- **Cards:** Rounded (16px), white on gray-50 background, 24px padding
- **Navigation:** 6 bottom tabs (Activities, Calendar, Tasks, Home, People, Devices)
- **Grid:** 2-column for rooms, horizontal scroll for scenes/filters

## Phase 1: Foundation Setup

### 1.1 Dashboard Structure
**Create new files:**
- `dashboards/mobile-redesign.yaml` - Main dashboard config
- `dashboards/mobile-redesign-theme.yaml` - Tailwind-inspired theme
- `dashboards/mobile-redesign-templates.yaml` - Mobile UI component templates
- `dashboards/mobile-views/` directory for view files

### 1.2 Theme Implementation
**Implement Tailwind CSS color system:**
- Light theme: White cards on `bg-gray-50` backdrop
- Dark theme support
- Blue primary (`#3b82f6`), semantic colors (green/red/orange status)
- Border radius: `16px` for cards
- Typography: System fonts with proper hierarchy

### 1.3 Navigation System
**Bottom tab navigation (6 tabs):**
- Activities (Timer icon) - Toby's checklists + activity tracking
- Calendar (Calendar icon) - Calendar with weather integration  
- Tasks (List icon) - Shopping list + family todo
- Home (Home icon) - Room controls + scenes
- People (Users icon) - Family member pages
- Devices (Smartphone icon) - Device management + battery status

## Phase 2: Component System

### 2.1 Card Templates
**Implement React-inspired card patterns:**

#### Room Cards (2-column grid)
- Colored backgrounds (`bg-blue-100`, `bg-pink-100`) per room
- Large temperature display
- Status indicators (3 colored dots for light/speaker/temp)
- Emoji icons for room types
- Touch-friendly sizing (min 44px targets)

#### Activity Cards (large gradient cards)
- Swimming/Hockey/Morning checklists
- Progress tracking with large numbers
- Background overlay icons
- Hover animations (where possible in Lovelace)

#### Scene Control Pills
- Horizontal scrolling row
- Rounded pill buttons (`border-radius: 20px`)
- Icons + labels for each scene
- Active state styling

### 2.2 List Components
**Task management interface:**
- Checkboxes with real-time state updates
- Section separation (active/completed)
- Full-width input forms with blue accents
- Interactive shopping list management

### 2.3 Statistics Cards
**3-column metrics layout:**
- Large numbers with descriptive text
- Centered content alignment
- Progress indicators where applicable
- Device battery levels and status

## Phase 3: View Implementation

### 3.1 Home View (Smart Home Control)
**Layout structure:**
```
- Scene controls (horizontal scroll pills)
- Room grid (2-column)
  - Whole House (indigo #6366f1)
  - Living Room (pink #ec4899) 
  - Kitchen (teal #14b8a6)
  - Bedroom (purple #8b5cf6)
  - Toby's Room (amber #f59e0b)
  - Outside (lime #84cc16)
- Quick actions (2x2 grid)
```

**Preserve all tablet functionality:**
- Temperature sensors and display
- Light controls with brightness/color
- Speaker controls
- Scene activation
- Roomba integration
- Camera feeds

### 3.2 Activities View (Toby's Features)
**Activity tracking interface:**
- Large feature cards for Swimming/Hockey
- Progress statistics
- Interactive checklists
- Timer integration
- Motivational progress messages

### 3.3 Tasks View
**Dual-list interface:**
- Shopping list (`todo.google_keep_shopping_list`)
- Family todo (`todo.google_keep_family_todo`)
- Add/edit/complete functionality
- Category organization

### 3.4 Calendar View
**Weather + events interface:**
- Weather cards (horizontal scroll)
- Week/month toggle preservation
- Event timeline with color coding
- Add event functionality
- Filter controls (pill buttons)

### 3.5 People View
**Family management:**
- Avatar system (colored circles)
- Status indicators (online/offline)
- Individual person pages
- Action cards for each family member

### 3.6 Devices View
**Device management:**
- Category filters (horizontal scroll)
- Device cards with status
- Battery level monitoring
- Find device functionality
- Network statistics (3-column layout)

## Phase 4: Mobile Optimizations

### 4.1 Touch Interface
- Minimum 44px touch targets
- Appropriate spacing (24px container padding)
- Gesture support where possible
- Responsive grid systems

### 4.2 Performance
- Optimized card templates
- Efficient entity updates
- Minimal resource loading
- Mobile-friendly animations

### 4.3 Progressive Web App
- App manifest for home screen installation
- Proper viewport configuration
- Touch icons and splash screens
- Offline functionality where applicable

## Phase 5: Advanced Features

### 5.1 State Management
- Dynamic color system based on device states
- Real-time status updates
- Conditional display logic
- Template sensors for complex calculations

### 5.2 Animations & Feedback
- Transition effects where supported
- Visual feedback for interactions
- Loading states
- Success/error indicators

### 5.3 Accessibility
- Proper ARIA labels
- High contrast support
- Voice control integration
- Screen reader compatibility

## Implementation Strategy

### Priority 1 (Core Functionality)
1. Dashboard structure and navigation
2. Theme implementation 
3. Room control system
4. Basic card templates

### Priority 2 (Feature Parity)
1. Tasks and calendar views
2. Device management
3. People interface
4. Activity tracking

### Priority 3 (Polish)
1. Animations and transitions
2. Advanced mobile features
3. Performance optimizations
4. Accessibility enhancements

## Technical Requirements

### Custom Cards Needed
- `custom:button-card` (primary component system)
- `custom:layout-card` (responsive grids)
- `custom:mushroom-*` cards (modern controls)
- `custom:mini-graph-card` (statistics)
- `card-mod` (styling)

### Home Assistant Integrations
- All existing entities preserved
- Additional input helpers for navigation state
- Template sensors for dynamic styling
- Scripts for complex interactions

### Configuration Updates
- Add new dashboard to `configuration.yaml`
- Install required custom cards
- Configure mobile theme
- Set up navigation helpers

## Entity Mapping (Preserve from Tablet)

### Rooms & Entities
- **Whole House:** `sensor.living_room_temp_temperature`, `media_player.speakers`, multiple lights
- **Living Room:** `light.living_room_color`, `light.extended_color_light_1`, temperature sensor
- **Kitchen:** `light.dining_kitchen_zone`, `light.kitchen_table`, `light.kitchen`, `vacuum.roomba_mcroomba`
- **Bedroom:** `light.master_bedroom`, `sensor.bedroom_temp_humidity_temperature`
- **Toby's Room:** `light.toby_s_room`, `sensor.toby_s_room_temp_temperature_2`
- **Outside:** `light.outdoor_plug`, `sensor.outside_temperature_temperature`, `camera.front_yard_camera`, `binary_sensor.outside_door`

### Scenes & Scripts
- `scene.front_house_relax`, `scene.front_house_concentrate`, `scene.front_house_nightlight`
- `script.good_morning_sequence`, `script.good_night_sequence`

### Tasks & Calendar
- `todo.google_keep_shopping_list`, `todo.google_keep_family_todo`
- `calendar.home_calendar`, `calendar.meals`, `calendar.holidays_in_united_states`
- `weather.home`

### Devices & People
- Phone tracking: `device_tracker.iphone`, `device_tracker.pixel_7`
- Battery sensors: `sensor.iphone_battery_level`, `sensor.pixel_7_battery_level`
- Tablets: `device_tracker.benjamins_ipad`, `sensor.benjamins_ipad_battery_level`

### Activity Tracking (Toby's Features)
- Input booleans for checklists: swimming, hockey, morning routines
- Timer integrations and progress tracking

---

**Created:** $(date)
**Status:** Planning Phase
**Next Step:** Phase 1.1 - Dashboard Structure Setup