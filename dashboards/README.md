# Home Assistant Mobile Dashboard

This mobile dashboard is designed to provide an optimized experience for mobile devices, with a focus on usability and performance.

## Features

- **Top Navigation**: Easy access to Home, Calendar, and Devices views
- **Mobile-Optimized UI**: Larger touch targets, improved readability, and simplified controls
- **Responsive Design**: Adapts to different mobile screen sizes
- **Swipe Navigation**: Navigate between views with swipe gestures
- **Optimized Cards**: Custom card templates designed specifically for mobile use

## Views

1. **Home View**
   - Quick actions for commonly used controls
   - Status overview with key information
   - Room cards with temperature and light status

2. **Calendar View**
   - Week view of your calendar events
   - Optimized for mobile viewing

3. **Devices View**
   - Categorized device controls (Lights, Climate, Security)
   - Smart device cards for media players and other devices

## Templates

The dashboard uses several custom templates:

- `mobile_top_nav`: Navigation bar template
- `mobile_room_card`: Room card optimized for mobile
- `mobile_device_card`: Device card optimized for mobile
- `quick_action`: Quick action buttons
- `heading`: Section headings

## Theme

The dashboard uses the `mobile-optimized` theme which includes:

- Larger touch targets
- Improved readability
- Better contrast
- Optimized scrolling
- Enhanced tap feedback

## Setup

1. Make sure you have the required custom cards installed:
   - button-card
   - vertical-stack-in-card
   - mushroom cards
   - browser_mod

2. Add the input_text entities to your configuration.yaml:
   ```yaml
   input_text:
     mobile_home_view:
       name: Mobile Home View
       initial: mobile-home
       icon: mdi:home
     mobile_calendar_view:
       name: Mobile Calendar View
       initial: mobile-calendar
       icon: mdi:calendar-month
     mobile_devices_view:
       name: Mobile Devices View
       initial: mobile-devices
       icon: mdi:devices
   ```

3. Restart Home Assistant to apply the changes

4. Access the dashboard at: `/mobile-dashboard/mobile-home`

## Customization

You can customize this dashboard by:

- Editing the `mobile.yaml` file to change the layout or add/remove cards
- Modifying the templates in `button_card_templates.yaml`
- Adjusting the theme in `themes/mobile-optimized.yaml`

## Tips for Mobile Use

- Use the swipe navigation to move between views
- Tap on room or device cards to access detailed controls
- Use the quick actions for frequently used controls
- The calendar view is optimized for weekly planning 