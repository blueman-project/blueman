# PROJECT: BLUEMAN NEXT
## Complete GTK+ UI Modernization, Rebranding & Bug Fixing

### SOURCE REPOSITORIES

Our existing fork:
https://github.com/nirodg/blueman

Original upstream:
https://github.com/blueman-project/blueman

### PROJECT OBJECTIVE

You are a Principal GTK+ Developer, Python Engineer,
Linux Desktop Engineer, UI/UX Designer, and Software Architect.

Your task is to modernize and rebrand our EXISTING Blueman fork.

We want to transform the traditional Blueman Bluetooth Manager
into a premium, Apple-inspired, 2026-generation Linux application.

The application should feature:

- Beautiful macOS-inspired aesthetics
- Modern glass-like surfaces
- Premium dark and light themes
- Smooth native GTK animations
- Modern device management cards
- Redesigned navigation
- Improved Bluetooth device discovery
- Better pairing experiences
- Modern device information panels
- Improved notifications
- Comprehensive bug fixing
- Better accessibility
- Improved responsiveness
- Native Linux desktop integration

IMPORTANT:

THIS IS NOT A NEW APPLICATION.

DO NOT rewrite the application using React, Tauri, Electron,
Qt, Flutter, or web technologies.

DO NOT replace the existing BlueZ backend.

DO NOT unnecessarily rewrite existing Bluetooth functionality.

We are modernizing an existing GTK+ application.

Preserve the existing Python, GTK, GObject, Gio, GLib,
and BlueZ architecture wherever possible.

============================================================
1. MANDATORY REPOSITORY ANALYSIS
============================================================

Before making any modifications, thoroughly inspect
the existing repository.

Identify:

1. Current GTK version.
2. Current Python version requirements.
3. Existing UI definitions.
4. Existing Gtk.Builder XML files.
5. Existing CSS styling.
6. Existing application entry points.
7. Existing Bluetooth manager architecture.
8. Existing BlueZ integration.
9. Existing D-Bus services.
10. Existing plugin architecture.
11. Existing system tray implementation.
12. Existing settings and GSettings schemas.
13. Existing notification infrastructure.
14. Existing pairing functionality.
15. Existing file transfer functionality.
16. Existing audio device management.
17. Existing build and packaging system.
18. Existing automated tests.
19. Existing bugs and FIXME/TODO comments.
20. Differences between our fork and upstream.

Pay particular attention to these upstream components
when they exist in our fork:

blueman/main/Manager.py

blueman/gui/manager/ManagerDeviceList.py

blueman/gui/manager/ManagerToolbar.py

blueman/gui/manager/ManagerMenu.py

blueman/gui/manager/ManagerStats.py

blueman/gui/manager/ManagerProgressbar.py

blueman/main/Builder.py

blueman/bluez/

blueman/plugins/

data/

Do not assume our fork is identical to upstream.

Inspect the actual local implementation.

Produce an architectural assessment before implementing changes.

============================================================
2. FRAMEWORK STRATEGY
============================================================

The existing application uses GTK+.

Our preferred approach is to preserve the current GTK version.

If the repository uses GTK 3:

- Continue using GTK 3.
- Continue using PyGObject.
- Use Gtk.Builder XML.
- Use GTK CSS.
- Use Gtk.StyleContext.
- Use GLib animation timers where appropriate.
- Use Gtk.Revealer.
- Use Gtk.Stack.
- Use Gtk.StackSwitcher where appropriate.
- Use Gtk.Overlay.
- Use Gtk.ListBox.
- Use Gtk.ScrolledWindow.
- Use Gtk.HeaderBar when suitable.
- Use Cairo for custom drawing where justified.

DO NOT migrate to GTK 4 without explicit approval.

DO NOT introduce Libadwaita as a mandatory dependency.

GTK 4 migration is a separate architectural project.

All UI improvements must work within the existing
GTK architecture.

============================================================
3. DESIGN PHILOSOPHY
============================================================

Visual direction:

Apple macOS meets a futuristic 2026 Linux desktop.

The interface should feel:

- Premium
- Minimal
- Elegant
- Fluid
- Modern
- Responsive
- Carefully crafted
- Consistent
- Lightweight

Visual inspiration:

- macOS System Settings
- Apple Control Center
- macOS Sonoma / Sequoia design language
- Modern translucent desktop interfaces
- Premium productivity applications

Avoid:

- Legacy GTK appearance
- Old-fashioned toolbars
- Excessive separators
- Dense technical lists
- Tiny action buttons
- Outdated icons
- Excessive menus
- Heavy gradients
- Excessive neon effects
- Unnecessary animations

Use native GTK widgets wherever possible.

Do not sacrifice usability for aesthetics.

============================================================
4. REBRANDING SYSTEM
============================================================

The application must support a complete rebrand.

IMPORTANT:

The final brand name has not yet been specified.

Create centralized branding configuration so the
product can be renamed without editing dozens of files.

Branding must include:

- Application display name
- Application icon
- Application description
- About dialog
- Window title
- Desktop launcher
- AppStream metadata
- Notification identity
- Documentation
- Application screenshots
- Package display metadata

Separate visual branding from internal application identity.

DO NOT immediately rename:

- D-Bus service names
- GSettings schema IDs
- Executable names
- Python packages
- Systemd units
- Plugin identifiers

These may be referenced throughout the existing application.

First audit all references and dependencies.

Create a separate migration plan for internal identifiers.

The initial redesign must remain compatible with
existing installations and configuration data.

Preserve GPL licensing and required copyright notices.

============================================================
5. GLOBAL GTK DESIGN SYSTEM
============================================================

Create a centralized visual design system.

Suggested structure:

blueman/gui/theme/
    __init__.py
    ThemeManager.py
    AnimationManager.py
    DesignTokens.py

data/themes/
    dark.css
    light.css
    components.css
    animations.css

Adapt these paths to the actual repository structure.

Do not create unnecessary abstractions.

------------------------------------------------------------
5.1 COLOR SYSTEM
------------------------------------------------------------

Dark theme:

Primary background:
#0B1118

Secondary background:
#121B25

Card background:
#1A2532

Elevated background:
#202D3C

Primary accent:
#477BFF

Secondary accent:
#7C5CFF

Connected:
#42D98B

Warning:
#FFB84D

Disconnected:
#8B95A7

Error:
#FF6475

Primary text:
#F5F7FB

Secondary text:
#A2ADBE

Muted text:
#697587

Borders:
rgba(255,255,255,0.09)

Selected border:
rgba(92,143,255,0.75)

Light theme:

Use a complementary premium Apple-inspired palette.

Ensure proper contrast in both themes.

------------------------------------------------------------
5.2 GTK CSS
------------------------------------------------------------

Implement reusable GTK CSS classes.

Examples:

.app-window

.app-sidebar

.sidebar-navigation

.sidebar-item

.sidebar-item-active

.glass-panel

.device-card

.device-card-selected

.device-card-connected

.device-card-disconnected

.device-avatar

.device-name

.device-subtitle

.device-status

.primary-button

.secondary-button

.danger-button

.inspector-panel

.search-entry

.status-indicator

.battery-indicator

Implement rounded corners, gradients, borders,
hover effects, and selected states using GTK CSS.

Example:

.device-card {
    background-color: #1A2532;
    border-radius: 18px;
    border: 1px solid alpha(white, 0.08);
    padding: 16px;
}

.device-card:hover {
    background-color: #202D3C;
    border-color: alpha(white, 0.16);
}

.device-card-selected {
    background-color: #1B2D49;
    border-color: #477BFF;
}

Adapt CSS syntax to the supported GTK version.

Do not assume browser CSS capabilities.

GTK CSS is not equivalent to web CSS.

------------------------------------------------------------
5.3 GLASSMORPHISM
------------------------------------------------------------

Implement a GTK-compatible approximation of
premium translucent surfaces.

Use:

- Semi-transparent backgrounds
- Subtle gradients
- Rounded corners
- Thin borders
- Layered surfaces
- Carefully controlled shadows
- Soft ambient accent colors

IMPORTANT:

GTK 3 does not provide a universal equivalent
of CSS backdrop-filter.

Do not implement fragile compositor-specific blur hacks.

Do not make the interface dependent on GNOME,
KDE, X11, or Wayland-specific blur behavior.

If true background blur is unavailable,
use elegant opaque or semi-transparent surfaces.

The application must remain visually attractive
without compositor blur.

============================================================
6. MAIN APPLICATION WINDOW
============================================================

Redesign the existing Bluetooth Manager window.

Component:

ModernManagerWindow

Recommended default size:
1400 x 850

Minimum size:
900 x 600

Layout:

+-----------------------------------------------------------+
| Header / Window Controls                                  |
+--------------+-------------------------+------------------+
|              |                         |                  |
| Sidebar      | Device Dashboard        | Device Inspector |
|              |                         |                  |
|              |                         |                  |
|              |                         |                  |
+--------------+-------------------------+------------------+

Three primary regions:

1. Navigation sidebar
2. Main device dashboard
3. Device inspector

Use:

Gtk.Box
Gtk.Paned
Gtk.Overlay
Gtk.ScrolledWindow

Choose widgets based on actual requirements.

Do not attempt to recreate CSS Grid.

The layout must resize correctly.

Persist window size using existing GSettings
where possible.

------------------------------------------------------------
6.1 CUSTOM HEADER
------------------------------------------------------------

Replace the traditional menu-heavy header with
a modern application header.

Preferred widget:
Gtk.HeaderBar

Contents:

Left:
Application identity or navigation control.

Center:
Application title.

Right:
- Bluetooth status
- Search
- Settings
- Window controls where provided by GTK

Use client-side decorations where supported.

Respect the user's desktop environment.

Do not hardcode macOS traffic-light controls
if this conflicts with native window management.

The visual style may be Apple-inspired,
but functionality must remain native to Linux.

============================================================
7. LEFT SIDEBAR
============================================================

Component:

ModernSidebar

Recommended width:
260px

Appearance:

- Dark elevated surface
- Subtle right border
- Rounded navigation selections
- Consistent spacing
- Premium iconography

Sections:

Application Identity

Navigation

Bluetooth Controller

Adapter Information

------------------------------------------------------------
7.1 APPLICATION IDENTITY
------------------------------------------------------------

Display:

[Bluetooth Icon] Bluetooth
                 2 devices connected

Use the actual connected device count.

The Bluetooth icon should use a blue gradient
inside a rounded square.

Use symbolic icons or bundled SVG resources.

------------------------------------------------------------
7.2 NAVIGATION
------------------------------------------------------------

Items:

Devices
Scan
Files
Settings

Each item:

- Icon
- Label
- Active state
- Hover state
- Keyboard focus state

Recommended height:
46px

Use Gtk.ListBox or equivalent native widgets.

Active item:

- Blue-tinted background
- Rounded corners
- Subtle accent border

Switch pages using Gtk.Stack.

Animate page transitions using supported
Gtk.Stack transition types.

------------------------------------------------------------
7.3 BLUETOOTH POWER CONTROLLER
------------------------------------------------------------

Display a premium controller card.

Contents:

Bluetooth

[ON/OFF SWITCH]

Visible as:
<Adapter Name>

Use Gtk.Switch.

Bind the switch to the existing
Bluetooth power management implementation.

Do not duplicate adapter power logic.

Handle:

- Adapter unavailable
- Adapter blocked
- Bluetooth disabled
- Power transition pending
- D-Bus errors

The UI must always reflect actual adapter state.

------------------------------------------------------------
7.4 BLUETOOTH RADAR
------------------------------------------------------------

Create an animated Bluetooth radar.

Use a custom Gtk.DrawingArea and Cairo
only where necessary.

Visual:

Central Bluetooth icon.

Three concentric circular rings.

Idle:
Subtle static rings.

Scanning:
Expanding radar waves.

Connected:
Gentle breathing animation.

Disabled:
Gray inactive appearance.

Animation:

Use GLib.timeout_add or an appropriate
GTK frame-clock mechanism.

Target:
Approximately 30 FPS for decorative animations.

Use frame-clock timing when smooth animation
requires synchronization with rendering.

Stop animation when:

- Widget is hidden
- Bluetooth is disabled
- Window is not visible
- Reduced motion is enabled

Avoid unnecessary CPU usage.

============================================================
8. MAIN DASHBOARD
============================================================

Component:

ModernDeviceDashboard

Contents:

1. Search
2. Dashboard header
3. Connected devices
4. Paired devices
5. Available devices

Use Gtk.ScrolledWindow.

Maintain a clear visual hierarchy.

------------------------------------------------------------
8.1 SEARCH BAR
------------------------------------------------------------

Use Gtk.SearchEntry.

Placeholder:

"Search devices, files, or actions..."

Keyboard shortcut:
Ctrl + K

Features:

- Search by device name
- Search by MAC address
- Filter connected devices
- Filter paired devices
- Filter discovered devices

Search must be case-insensitive.

Use existing device data.

Do not initiate unnecessary D-Bus operations
on every keystroke.

------------------------------------------------------------
8.2 DASHBOARD HEADER
------------------------------------------------------------

Title:

Bluetooth Devices

Subtitle:

Manage your connected devices, send files, and more.

Right:

Primary action button:

+ Pair New Device

Use existing device discovery functionality.

------------------------------------------------------------
8.3 CONNECTED DEVICES
------------------------------------------------------------

Header:

Connected (N)

Display devices currently connected.

Use actual BlueZ connection state.

Device cards should appear in a vertical list.

------------------------------------------------------------
8.4 PAIRED DEVICES
------------------------------------------------------------

Header:

Paired Devices (N)

Display paired devices that are not connected.

Actions:

Connect
Forget
Trust / Untrust

------------------------------------------------------------
8.5 AVAILABLE DEVICES
------------------------------------------------------------

Header:

Available Devices (N)

Display newly discovered devices.

Actions:

Pair
Refresh

Do not confuse paired and discovered states.

============================================================
9. DEVICE CARD COMPONENT
============================================================

Component:

ModernDeviceCard

This is a critical component.

Replace the traditional technical device list
with premium interactive cards.

Recommended card height:
120–150px

Card layout:

+-------------------------------------------------------+
|                                                       |
| [Device Icon] Device Name               [Actions]     |
|               Device Type                             |
|               MAC Address                             |
|                                                       |
|               ● Connected   Battery 80%               |
|                                                       |
+-------------------------------------------------------+

------------------------------------------------------------
9.1 DEVICE AVATAR
------------------------------------------------------------

Size:
72 x 72px

Rounded corners:
16px

Device categories:

- Speaker
- Headphones
- Smartphone
- Keyboard
- Mouse
- Controller
- Computer
- Unknown

Use symbolic SVG illustrations.

Use different subtle accent backgrounds
for each device category.

Do not fetch device artwork from the internet.

------------------------------------------------------------
9.2 DEVICE NAME
------------------------------------------------------------

Use actual BlueZ device alias.

Font:
16px semibold.

Truncate long names gracefully.

Show full name in tooltip.

------------------------------------------------------------
9.3 DEVICE TYPE
------------------------------------------------------------

Examples:

Loudspeaker
Headset
Smartphone
Keyboard
Mouse

Use existing device classification logic.

Do not create a second classification system
unless necessary.

------------------------------------------------------------
9.4 MAC ADDRESS
------------------------------------------------------------

Display actual device address.

Provide copy-to-clipboard action.

Use Gtk.Clipboard or supported Gio APIs.

------------------------------------------------------------
9.5 CONNECTION STATUS
------------------------------------------------------------

States:

Connected:
Green indicator.

Disconnected:
Gray indicator.

Connecting:
Animated blue indicator.

Pairing:
Purple indicator.

Error:
Red indicator.

Status must reflect actual backend state.

------------------------------------------------------------
9.6 BATTERY
------------------------------------------------------------

Display:

Battery icon
Percentage

Only when actual battery information is available.

Reuse existing battery monitoring functionality.

Never fabricate percentages.

------------------------------------------------------------
9.7 QUICK ACTIONS
------------------------------------------------------------

Provide:

Connect
Disconnect
Pair
Send File
More

Actions must be context-aware.

Use existing Blueman functionality.

Do not duplicate D-Bus calls unnecessarily.

------------------------------------------------------------
9.8 SELECTION
------------------------------------------------------------

When selected:

- Apply blue border
- Change card background
- Update inspector
- Preserve keyboard focus

Selecting a card must not automatically
connect the device.

------------------------------------------------------------
9.9 CARD ANIMATIONS
------------------------------------------------------------

Implement subtle animations.

Hover:
Background transition.

Selection:
Accent transition.

Connection:
Status indicator animation.

Discovery:
Fade-in where practical.

GTK 3 does not support arbitrary CSS transforms
like a web browser.

Use native GTK mechanisms.

Avoid unnecessary custom animation frameworks.

============================================================
10. DEVICE INSPECTOR
============================================================

Component:

ModernDeviceInspector

Position:
Right side.

Recommended width:
340px

Display details for selected device.

Sections:

Device Identity

Connection Status

Quick Actions

Device Information

Additional Actions

------------------------------------------------------------
10.1 DEVICE HEADER
------------------------------------------------------------

Display:

Large device avatar.

Device name.

Device category.

Rename action where supported.

------------------------------------------------------------
10.2 CONNECTION STATUS
------------------------------------------------------------

Display:

Connected / Disconnected / Connecting

Battery percentage if available.

------------------------------------------------------------
10.3 QUICK ACTIONS
------------------------------------------------------------

Three large action buttons:

Audio
Send File
More

Use premium rounded buttons.

Audio:

Reuse existing Blueman audio integration.

Do not create a new audio backend unless necessary.

Send File:

Reuse existing OBEX transfer functionality.

More:

Open existing device actions in a modern popover.

------------------------------------------------------------
10.4 DEVICE INFORMATION
------------------------------------------------------------

Display:

Bluetooth Address

Device Type

Bluetooth Class

Connected

Paired

Trusted

RSSI when available

Battery when available

Adapter

Supported services where available

Do not invent metadata.

If a property is unavailable,
hide it or display an appropriate placeholder.

------------------------------------------------------------
10.5 QUICK ACTIONS PANEL
------------------------------------------------------------

Actions:

Open Sound Settings

Forget Device

Additional actions based on device capabilities.

Forget Device:

Require confirmation.

============================================================
11. DEVICE PAIRING EXPERIENCE
============================================================

Modernize the existing pairing workflow.

Do not replace the underlying pairing implementation.

Create a modern GTK dialog or overlay.

States:

Discovering

Device Selected

Pairing

Authorization Required

Connected

Failed

------------------------------------------------------------
11.1 DISCOVERY
------------------------------------------------------------

Display animated radar.

Text:

Searching for nearby devices...

Show discovered devices in real time.

------------------------------------------------------------
11.2 PAIRING
------------------------------------------------------------

Display:

Device avatar

Device name

Pairing status

Use Gtk.Spinner or native progress indication.

Do not invent pairing percentages.

------------------------------------------------------------
11.3 AUTHORIZATION
------------------------------------------------------------

Preserve all existing pairing agent functionality.

Support:

PIN entry

Passkey confirmation

Passkey display

Authorization requests

Pairing cancellation

Do not automatically approve security prompts.

------------------------------------------------------------
11.4 SUCCESS
------------------------------------------------------------

Display:

Device paired successfully.

Provide:

Done

View Device

------------------------------------------------------------
11.5 FAILURE
------------------------------------------------------------

Display meaningful errors.

Examples:

Authentication rejected

Device unavailable

Pairing timed out

Connection failed

Allow retry where appropriate.

============================================================
12. FILE TRANSFER
============================================================

Modernize the existing OBEX transfer interface.

Preserve existing functionality.

Display:

Destination device

File name

File size

Transfer progress

Transfer speed when available

Remaining time when calculable

States:

Preparing

Connecting

Transferring

Completed

Failed

Cancelled

Use Gtk.ProgressBar.

Use native file chooser dialogs.

Support cancellation.

Do not simulate transfer progress.

============================================================
13. NOTIFICATIONS
============================================================

Improve existing notification handling.

Support:

Device connected

Device disconnected

Pairing succeeded

Pairing failed

File transfer completed

File transfer failed

Bluetooth adapter unavailable

Battery low when supported

Use the existing notification infrastructure
and desktop notification integration.

Avoid duplicate notifications.

Provide contextual error messages.

Use Gtk.Revealer for inline notification banners
where appropriate.

============================================================
14. SETTINGS
============================================================

Modernize existing settings dialogs.

Use Gtk.Stack, Gtk.ListBox, and native controls.

Sections:

General

Bluetooth Adapter

Appearance

Notifications

Advanced

------------------------------------------------------------
14.1 GENERAL
------------------------------------------------------------

Launch on startup

Minimize to tray

Close to tray

Automatic reconnection

Only expose options actually supported.

------------------------------------------------------------
14.2 ADAPTER
------------------------------------------------------------

Adapter selection

Bluetooth power

Discoverable

Pairable

Adapter alias

Adapter address

------------------------------------------------------------
14.3 APPEARANCE
------------------------------------------------------------

Theme:

Dark

Light

System

Options:

Enable animations

Reduce motion

Compact device cards

Ambient background effects

Persist preferences using GSettings.

------------------------------------------------------------
14.4 ADVANCED
------------------------------------------------------------

Show technical device information.

Enable debug logging.

View diagnostic information.

Display BlueZ service status.

============================================================
15. ANIMATION ENGINE
============================================================

Implement a lightweight reusable animation system.

Use:

Gtk.Revealer

Gtk.Stack transitions

Gtk.ProgressBar

Gtk.Spinner

GLib timers

GTK frame clock

Cairo where appropriate

Animations:

Sidebar selection

Page transitions

Device discovery

Connection state

Pairing progress

Bluetooth radar

Notification appearance

Dialog transitions

IMPORTANT:

GTK 3 animations differ from browser animations.

Do not attempt to implement Framer Motion concepts
directly in GTK.

Use native GTK mechanisms.

All animations must:

- Be lightweight
- Avoid blocking the GTK main loop
- Respect reduced motion
- Stop when unnecessary
- Avoid memory leaks
- Avoid excessive CPU usage

============================================================
16. BUG FIXING STRATEGY
============================================================

Perform a systematic bug audit.

Inspect:

- Existing GitHub issues
- Existing FIXME comments
- Existing TODO comments
- Error handling
- D-Bus signal subscriptions
- Bluetooth discovery lifecycle
- Device connection lifecycle
- Pairing callbacks
- Plugin initialization
- GTK signal handlers
- Notification handling
- File transfers
- Adapter switching
- Application shutdown
- BlueZ service restarts

Compare relevant upstream fixes with our fork.

Do not blindly merge upstream changes.

For every identified bug:

1. Describe the issue.
2. Identify the root cause.
3. Determine affected components.
4. Create a regression test where feasible.
5. Implement the smallest safe fix.
6. Verify the fix.
7. Document the change.

Prioritize:

P0:
Crashes, data loss, security issues.

P1:
Broken Bluetooth functionality.

P2:
Incorrect UI states and workflow bugs.

P3:
Visual inconsistencies and minor UX problems.

============================================================
17. PRESERVE EXISTING FUNCTIONALITY
============================================================

The redesign must preserve:

Bluetooth adapter management

Bluetooth device discovery

Device pairing

Device connection

Device disconnection

Trusted devices

Device removal

Audio profiles

Bluetooth audio integration

OBEX file transfers

Bluetooth networking

Input devices

Serial services where supported

System tray functionality

Existing plugins

D-Bus services

Desktop notifications

GSettings preferences

Existing command-line interfaces

Do not remove functionality merely because
it is not visible in the redesigned dashboard.

Advanced functionality may remain accessible
through contextual menus or advanced settings.

============================================================
18. PLUGIN COMPATIBILITY
============================================================

Blueman has an existing plugin architecture.

Preserve compatibility with existing plugins.

Inspect:

Manager plugins

Applet plugins

Service plugins

Plugin registration

Plugin activation

Plugin settings

Do not break existing extension points.

If the redesigned device list changes
existing widget interfaces, create compatibility
adapters where practical.

Document unavoidable breaking changes.

============================================================
19. PERFORMANCE
============================================================

Requirements:

Fast startup.

Low idle CPU usage.

Low memory overhead.

Responsive GTK main loop.

No blocking D-Bus operations on the UI thread.

No unnecessary polling.

Efficient device list updates.

Avoid recreating all device cards on every
property change.

Update only affected widgets where possible.

Stop hidden animations.

Clean up signal handlers and GLib sources.

============================================================
20. ACCESSIBILITY
============================================================

Support:

Keyboard navigation

Accessible widget labels

Screen readers

Visible focus states

High contrast

Reduced motion

Tooltips

Logical focus order

Accessible dialogs

Preserve existing keyboard shortcuts
unless there is a documented reason to change them.

============================================================
21. BUILD SYSTEM
============================================================

Preserve the repository's existing build system.

Inspect whether the fork uses:

Meson

Autotools

Or both.

Do not replace the build system unnecessarily.

Update resource manifests for:

GTK CSS

SVG icons

Gtk.Builder UI definitions

Theme resources

Branding assets

Ensure all resources are installed correctly.

============================================================
22. TESTING
============================================================

Run existing tests before making changes.

Establish a baseline.

After changes, verify:

Application startup

Window rendering

Adapter detection

Bluetooth enable/disable

Device discovery

Device pairing

Device connection

Device disconnection

Device removal

File transfer

Audio profiles

System tray

Plugin loading

Settings persistence

Theme switching

Application shutdown

BlueZ service recovery

Use mocks for automated tests where appropriate.

Do not ship mock device data in production.

============================================================
23. IMPLEMENTATION PHASES
============================================================

PHASE 0 — REPOSITORY AUDIT

Inspect existing architecture.

Identify dependencies.

Identify existing bugs.

Compare with upstream.

Create implementation plan.

Do not modify production code yet.

Deliver:

ARCHITECTURE_AUDIT.md

BUG_AUDIT.md

IMPLEMENTATION_PLAN.md

------------------------------------------------------------

PHASE 1 — BRANDING FOUNDATION

Implement:

Centralized branding

Application display name configuration

New icon resource structure

Updated visual identity

Branding documentation

Preserve internal identifiers until migration is approved.

------------------------------------------------------------

PHASE 2 — DESIGN SYSTEM

Implement:

GTK CSS tokens

Dark theme

Light theme

Reusable visual components

Typography

Spacing

Rounded cards

Buttons

Status indicators

------------------------------------------------------------

PHASE 3 — MAIN WINDOW REDESIGN

Implement:

Modern header

Sidebar

Dashboard layout

Device inspector

Responsive resizing

Navigation transitions

------------------------------------------------------------

PHASE 4 — DEVICE CARDS

Implement:

Connected device cards

Paired device cards

Available device cards

Device avatars

Connection indicators

Battery indicators

Quick actions

Selection states

------------------------------------------------------------

PHASE 5 — DEVICE INSPECTOR

Implement:

Device identity

Device information

Connection status

Device actions

Context menus

------------------------------------------------------------

PHASE 6 — PAIRING AND DISCOVERY

Modernize:

Scanning interface

Pairing dialogs

Authorization dialogs

Connection progress

Error handling

Preserve existing backend logic.

------------------------------------------------------------

PHASE 7 — ANIMATIONS

Implement:

Bluetooth radar

Device discovery transitions

Status animations

Sidebar transitions

Notification transitions

Dialog transitions

------------------------------------------------------------

PHASE 8 — SETTINGS AND TRANSFERS

Modernize:

Settings

Adapter configuration

File transfer interface

Notification preferences

Appearance settings

------------------------------------------------------------

PHASE 9 — BUG FIXING

Fix verified issues.

Prioritize functional and stability problems.

Add regression tests.

------------------------------------------------------------

PHASE 10 — PRODUCTION HARDENING

Verify:

Performance

Accessibility

Packaging

Desktop integration

Plugin compatibility

D-Bus compatibility

Settings migration

Application stability

============================================================
24. ACCEPTANCE CRITERIA
============================================================

The final application must:

1. Build successfully from the existing repository.

2. Continue using the existing GTK architecture.

3. Preserve existing BlueZ integration.

4. Preserve existing Bluetooth functionality.

5. Preserve existing plugin compatibility wherever possible.

6. Present a completely redesigned premium interface.

7. Support modern dark and light themes.

8. Display real Bluetooth device information.

9. Support device discovery and pairing.

10. Provide modern interactive device cards.

11. Provide a functional device inspector.

12. Support native GTK animations.

13. Avoid fabricated device information.

14. Handle Bluetooth errors gracefully.

15. Avoid blocking the GTK main loop.

16. Maintain low idle CPU usage.

17. Respect Linux desktop environments.

18. Preserve existing configuration data.

19. Include regression tests for bug fixes.

20. Be suitable for production distribution.

============================================================
25. CLAUDE CODE EXECUTION INSTRUCTIONS
============================================================

IMPORTANT:

Start by inspecting the repository.

Do not immediately rewrite files.

Do not replace the application architecture.

Do not introduce another UI framework.

Do not migrate to GTK 4 without approval.

Do not replace the existing BlueZ implementation.

Do not remove plugins.

Do not break D-Bus interfaces.

Do not invent Bluetooth device data.

Do not implement visual-only controls.

Do not claim a bug is fixed without verification.

WORKFLOW:

1. Inspect repository.
2. Produce architecture audit.
3. Identify existing functionality.
4. Identify bugs and technical risks.
5. Create implementation plan.
6. Implement changes incrementally.
7. Run tests.
8. Verify Bluetooth functionality.
9. Fix regressions.
10. Document changes.

Work in small, reviewable commits.

Before each major architectural change,
explain why it is necessary.

Prefer incremental modernization over rewrites.

The finished application should feel like
a premium, carefully designed Linux desktop application.

It must remain a real, fully functional Bluetooth manager.

BEGIN WITH PHASE 0: REPOSITORY AUDIT.

One change I'd make to the execution order
Rather than asking Claude to implement all ten phases immediately, I would have it complete Phase 0 first, then implement Phases 1–4 together.
That gives you a working, visually redesigned Bluetooth Manager early, while leaving advanced dialogs, animations, and less frequently used features for subsequent iterations.
