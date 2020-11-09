import builtins
import typing
import cairo

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf
from gi.repository import Gio
from gi.repository import Pango


class AppLaunchContext(Gio.AppLaunchContext):

    @staticmethod
    def new() -> AppLaunchContext: ...  # type: ignore

    def set_desktop(self, desktop: builtins.int) -> None: ...

    def set_display(self, display: Display) -> None: ...

    def set_icon(self, icon: typing.Optional[Gio.Icon]) -> None: ...

    def set_icon_name(self, icon_name: typing.Optional[builtins.str]) -> None: ...

    def set_screen(self, screen: Screen) -> None: ...

    def set_timestamp(self, timestamp: builtins.int) -> None: ...


class Cursor(GObject.Object):

    def get_cursor_type(self) -> CursorType: ...

    def get_display(self) -> Display: ...

    def get_image(self) -> typing.Optional[GdkPixbuf.Pixbuf]: ...

    def get_surface(self) -> typing.Tuple[typing.Optional[cairo.Surface], builtins.float, builtins.float]: ...

    @staticmethod
    def new(cursor_type: CursorType, **kwargs) -> Cursor: ...  # type: ignore

    @staticmethod
    def new_for_display(display: Display, cursor_type: CursorType) -> Cursor: ...

    @staticmethod
    def new_from_name(display: Display, name: builtins.str) -> typing.Optional[Cursor]: ...

    @staticmethod
    def new_from_pixbuf(display: Display, pixbuf: GdkPixbuf.Pixbuf, x: builtins.int, y: builtins.int) -> Cursor: ...

    @staticmethod
    def new_from_surface(display: Display, surface: cairo.Surface, x: builtins.float, y: builtins.float) -> Cursor: ...

    def ref(self) -> Cursor: ...

    def unref(self) -> None: ...


class Device(GObject.Object):

    def get_associated_device(self) -> typing.Optional[Device]: ...

    def get_axes(self) -> AxisFlags: ...

    def get_axis_use(self, index_: builtins.int) -> AxisUse: ...

    def get_device_type(self) -> DeviceType: ...

    def get_display(self) -> Display: ...

    def get_has_cursor(self) -> builtins.bool: ...

    def get_key(self, index_: builtins.int) -> typing.Tuple[builtins.bool, builtins.int, ModifierType]: ...

    def get_last_event_window(self) -> typing.Optional[Window]: ...

    def get_mode(self) -> InputMode: ...

    def get_n_axes(self) -> builtins.int: ...

    def get_n_keys(self) -> builtins.int: ...

    def get_name(self) -> builtins.str: ...

    def get_position(self) -> typing.Tuple[Screen, builtins.int, builtins.int]: ...

    def get_position_double(self) -> typing.Tuple[Screen, builtins.float, builtins.float]: ...

    def get_product_id(self) -> typing.Optional[builtins.str]: ...

    def get_seat(self) -> Seat: ...

    def get_source(self) -> InputSource: ...

    def get_vendor_id(self) -> typing.Optional[builtins.str]: ...

    def get_window_at_position(self) -> typing.Tuple[typing.Optional[Window], builtins.int, builtins.int]: ...

    def get_window_at_position_double(self) -> typing.Tuple[typing.Optional[Window], builtins.float, builtins.float]: ...

    def grab(self, window: Window, grab_ownership: GrabOwnership, owner_events: builtins.bool, event_mask: EventMask, cursor: typing.Optional[Cursor], time_: builtins.int) -> GrabStatus: ...

    @staticmethod
    def grab_info_libgtk_only(display: Display, device: Device) -> typing.Tuple[builtins.bool, Window, builtins.bool]: ...

    def list_axes(self) -> typing.Sequence[Atom]: ...

    def list_slave_devices(self) -> typing.Optional[typing.Sequence[Device]]: ...

    def set_axis_use(self, index_: builtins.int, use: AxisUse) -> None: ...

    def set_key(self, index_: builtins.int, keyval: builtins.int, modifiers: ModifierType) -> None: ...

    def set_mode(self, mode: InputMode) -> builtins.bool: ...

    def ungrab(self, time_: builtins.int) -> None: ...

    def warp(self, screen: Screen, x: builtins.int, y: builtins.int) -> None: ...


class DeviceManager(GObject.Object):

    def get_client_pointer(self) -> Device: ...

    def get_display(self) -> typing.Optional[Display]: ...

    def list_devices(self, type: DeviceType) -> typing.Sequence[Device]: ...


class DevicePad(GObject.GInterface):

    def get_feature_group(self, feature: DevicePadFeature, feature_idx: builtins.int) -> builtins.int: ...

    def get_group_n_modes(self, group_idx: builtins.int) -> builtins.int: ...

    def get_n_features(self, feature: DevicePadFeature) -> builtins.int: ...

    def get_n_groups(self) -> builtins.int: ...


class DeviceTool(GObject.Object):

    def get_hardware_id(self) -> builtins.int: ...

    def get_serial(self) -> builtins.int: ...

    def get_tool_type(self) -> DeviceToolType: ...


class Display(GObject.Object):

    def beep(self) -> None: ...

    def close(self) -> None: ...

    def device_is_grabbed(self, device: Device) -> builtins.bool: ...

    def flush(self) -> None: ...

    def get_app_launch_context(self) -> AppLaunchContext: ...

    @staticmethod
    def get_default() -> typing.Optional[Display]: ...

    def get_default_cursor_size(self) -> builtins.int: ...

    def get_default_group(self) -> Window: ...

    def get_default_screen(self) -> Screen: ...

    def get_default_seat(self) -> Seat: ...

    def get_device_manager(self) -> typing.Optional[DeviceManager]: ...

    def get_event(self) -> typing.Optional[Event]: ...

    def get_maximal_cursor_size(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_monitor(self, monitor_num: builtins.int) -> typing.Optional[Monitor]: ...

    def get_monitor_at_point(self, x: builtins.int, y: builtins.int) -> Monitor: ...

    def get_monitor_at_window(self, window: Window) -> Monitor: ...

    def get_n_monitors(self) -> builtins.int: ...

    def get_n_screens(self) -> builtins.int: ...

    def get_name(self) -> builtins.str: ...

    def get_pointer(self) -> typing.Tuple[Screen, builtins.int, builtins.int, ModifierType]: ...

    def get_primary_monitor(self) -> typing.Optional[Monitor]: ...

    def get_screen(self, screen_num: builtins.int) -> Screen: ...

    def get_window_at_pointer(self) -> typing.Tuple[typing.Optional[Window], builtins.int, builtins.int]: ...

    def has_pending(self) -> builtins.bool: ...

    def is_closed(self) -> builtins.bool: ...

    def keyboard_ungrab(self, time_: builtins.int) -> None: ...

    def list_devices(self) -> typing.Sequence[Device]: ...

    def list_seats(self) -> typing.Sequence[Seat]: ...

    def notify_startup_complete(self, startup_id: builtins.str) -> None: ...

    @staticmethod
    def open(display_name: builtins.str) -> typing.Optional[Display]: ...

    @staticmethod
    def open_default_libgtk_only() -> typing.Optional[Display]: ...

    def peek_event(self) -> typing.Optional[Event]: ...

    def pointer_is_grabbed(self) -> builtins.bool: ...

    def pointer_ungrab(self, time_: builtins.int) -> None: ...

    def put_event(self, event: Event) -> None: ...

    def request_selection_notification(self, selection: Atom) -> builtins.bool: ...

    def set_double_click_distance(self, distance: builtins.int) -> None: ...

    def set_double_click_time(self, msec: builtins.int) -> None: ...

    def store_clipboard(self, clipboard_window: Window, time_: builtins.int, targets: typing.Optional[typing.Sequence[Atom]]) -> None: ...

    def supports_clipboard_persistence(self) -> builtins.bool: ...

    def supports_composite(self) -> builtins.bool: ...

    def supports_cursor_alpha(self) -> builtins.bool: ...

    def supports_cursor_color(self) -> builtins.bool: ...

    def supports_input_shapes(self) -> builtins.bool: ...

    def supports_selection_notification(self) -> builtins.bool: ...

    def supports_shapes(self) -> builtins.bool: ...

    def sync(self) -> None: ...

    def warp_pointer(self, screen: Screen, x: builtins.int, y: builtins.int) -> None: ...


class DisplayManager(GObject.Object):

    @staticmethod
    def get() -> DisplayManager: ...

    def get_default_display(self) -> typing.Optional[Display]: ...

    def list_displays(self) -> typing.Sequence[Display]: ...

    def open_display(self, name: builtins.str) -> typing.Optional[Display]: ...

    def set_default_display(self, display: Display) -> None: ...


class DragContext(GObject.Object):

    def finish(self, success: bool, del_: bool, time: int) -> None: ...

    def get_actions(self) -> DragAction: ...

    def get_dest_window(self) -> Window: ...

    def get_device(self) -> Device: ...

    def get_drag_window(self) -> typing.Optional[Window]: ...

    def get_protocol(self) -> DragProtocol: ...

    def get_selected_action(self) -> DragAction: ...

    def get_source_window(self) -> Window: ...

    def get_suggested_action(self) -> DragAction: ...

    def list_targets(self) -> typing.Sequence[Atom]: ...

    def manage_dnd(self, ipc_window: Window, actions: DragAction) -> builtins.bool: ...

    def set_device(self, device: Device) -> None: ...

    def set_hotspot(self, hot_x: builtins.int, hot_y: builtins.int) -> None: ...


class DrawingContext(GObject.Object):

    def get_cairo_context(self) -> cairo.Context: ...

    def get_clip(self) -> typing.Optional[cairo.Region]: ...

    def get_window(self) -> Window: ...

    def is_valid(self) -> builtins.bool: ...


class FrameClock(GObject.Object):

    def begin_updating(self) -> None: ...

    def end_updating(self) -> None: ...

    def get_current_timings(self) -> typing.Optional[FrameTimings]: ...

    def get_frame_counter(self) -> builtins.int: ...

    def get_frame_time(self) -> builtins.int: ...

    def get_history_start(self) -> builtins.int: ...

    def get_refresh_info(self, base_time: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_timings(self, frame_counter: builtins.int) -> typing.Optional[FrameTimings]: ...

    def request_phase(self, phase: FrameClockPhase) -> None: ...


class GLContext(GObject.Object):

    @staticmethod
    def clear_current() -> None: ...

    @staticmethod
    def get_current() -> typing.Optional[GLContext]: ...

    def get_debug_enabled(self) -> builtins.bool: ...

    def get_display(self) -> typing.Optional[Display]: ...

    def get_forward_compatible(self) -> builtins.bool: ...

    def get_required_version(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_shared_context(self) -> typing.Optional[GLContext]: ...

    def get_use_es(self) -> builtins.bool: ...

    def get_version(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_window(self) -> typing.Optional[Window]: ...

    def is_legacy(self) -> builtins.bool: ...

    def make_current(self) -> None: ...

    def realize(self) -> builtins.bool: ...

    def set_debug_enabled(self, enabled: builtins.bool) -> None: ...

    def set_forward_compatible(self, compatible: builtins.bool) -> None: ...

    def set_required_version(self, major: builtins.int, minor: builtins.int) -> None: ...

    def set_use_es(self, use_es: builtins.int) -> None: ...


class Keymap(GObject.Object):

    def add_virtual_modifiers(self, state: ModifierType) -> ModifierType: ...

    def get_caps_lock_state(self) -> builtins.bool: ...

    @staticmethod
    def get_default() -> Keymap: ...

    def get_direction(self) -> Pango.Direction: ...

    def get_entries_for_keycode(self, hardware_keycode: builtins.int) -> typing.Tuple[builtins.bool, typing.Sequence[KeymapKey], typing.Sequence[builtins.int]]: ...

    def get_entries_for_keyval(self, keyval: builtins.int) -> typing.Tuple[builtins.bool, typing.Sequence[KeymapKey]]: ...

    @staticmethod
    def get_for_display(display: Display) -> Keymap: ...

    def get_modifier_mask(self, intent: ModifierIntent) -> ModifierType: ...

    def get_modifier_state(self) -> builtins.int: ...

    def get_num_lock_state(self) -> builtins.bool: ...

    def get_scroll_lock_state(self) -> builtins.bool: ...

    def have_bidi_layouts(self) -> builtins.bool: ...

    def lookup_key(self, key: KeymapKey) -> builtins.int: ...

    def map_virtual_modifiers(self, state: ModifierType) -> typing.Tuple[builtins.bool, ModifierType]: ...

    def translate_keyboard_state(self, hardware_keycode: builtins.int, state: ModifierType, group: builtins.int) -> typing.Tuple[builtins.bool, builtins.int, builtins.int, builtins.int, ModifierType]: ...


class Monitor(GObject.Object):

    def get_display(self) -> Display: ...

    def get_geometry(self) -> Rectangle: ...

    def get_height_mm(self) -> builtins.int: ...

    def get_manufacturer(self) -> typing.Optional[builtins.str]: ...

    def get_model(self) -> typing.Optional[builtins.str]: ...

    def get_refresh_rate(self) -> builtins.int: ...

    def get_scale_factor(self) -> builtins.int: ...

    def get_subpixel_layout(self) -> SubpixelLayout: ...

    def get_width_mm(self) -> builtins.int: ...

    def get_workarea(self) -> Rectangle: ...

    def is_primary(self) -> builtins.bool: ...


class Screen(GObject.Object):

    def get_active_window(self) -> typing.Optional[Window]: ...

    @staticmethod
    def get_default() -> typing.Optional[Screen]: ...

    def get_display(self) -> Display: ...

    def get_font_options(self) -> typing.Optional[cairo.FontOptions]: ...

    def get_height(self) -> builtins.int: ...

    def get_height_mm(self) -> builtins.int: ...

    def get_monitor_at_point(self, x: builtins.int, y: builtins.int) -> builtins.int: ...

    def get_monitor_at_window(self, window: Window) -> builtins.int: ...

    def get_monitor_geometry(self, monitor_num: builtins.int) -> Rectangle: ...

    def get_monitor_height_mm(self, monitor_num: builtins.int) -> builtins.int: ...

    def get_monitor_plug_name(self, monitor_num: builtins.int) -> typing.Optional[builtins.str]: ...

    def get_monitor_scale_factor(self, monitor_num: builtins.int) -> builtins.int: ...

    def get_monitor_width_mm(self, monitor_num: builtins.int) -> builtins.int: ...

    def get_monitor_workarea(self, monitor_num: builtins.int) -> Rectangle: ...

    def get_n_monitors(self) -> builtins.int: ...

    def get_number(self) -> builtins.int: ...

    def get_primary_monitor(self) -> builtins.int: ...

    def get_resolution(self) -> builtins.float: ...

    def get_rgba_visual(self) -> typing.Optional[Visual]: ...

    def get_root_window(self) -> Window: ...

    def get_setting(self, name: builtins.str, value: GObject.Value) -> builtins.bool: ...

    def get_system_visual(self) -> Visual: ...

    def get_toplevel_windows(self) -> typing.Sequence[Window]: ...

    def get_width(self) -> builtins.int: ...

    def get_width_mm(self) -> builtins.int: ...

    def get_window_stack(self) -> typing.Optional[typing.Sequence[Window]]: ...

    @staticmethod
    def height() -> builtins.int: ...

    @staticmethod
    def height_mm() -> builtins.int: ...

    def is_composited(self) -> builtins.bool: ...

    def list_visuals(self) -> typing.Sequence[Visual]: ...

    def make_display_name(self) -> builtins.str: ...

    def set_font_options(self, options: typing.Optional[cairo.FontOptions]) -> None: ...

    def set_resolution(self, dpi: builtins.float) -> None: ...

    @staticmethod
    def width() -> builtins.int: ...

    @staticmethod
    def width_mm() -> builtins.int: ...


class Seat(GObject.Object):
    parent_instance: GObject.Object

    def get_capabilities(self) -> SeatCapabilities: ...

    def get_display(self) -> Display: ...

    def get_keyboard(self) -> typing.Optional[Device]: ...

    def get_pointer(self) -> typing.Optional[Device]: ...

    def get_slaves(self, capabilities: SeatCapabilities) -> typing.Sequence[Device]: ...

    def grab(self, window: Window, capabilities: SeatCapabilities, owner_events: builtins.bool, cursor: typing.Optional[Cursor], event: typing.Optional[Event], prepare_func: typing.Optional[SeatGrabPrepareFunc], *prepare_func_data: typing.Optional[builtins.object]) -> GrabStatus: ...

    def ungrab(self) -> None: ...


class Visual(GObject.Object):

    @staticmethod
    def get_best() -> Visual: ...

    @staticmethod
    def get_best_depth() -> builtins.int: ...

    @staticmethod
    def get_best_type() -> VisualType: ...

    @staticmethod
    def get_best_with_both(depth: builtins.int, visual_type: VisualType) -> typing.Optional[Visual]: ...

    @staticmethod
    def get_best_with_depth(depth: builtins.int) -> Visual: ...

    @staticmethod
    def get_best_with_type(visual_type: VisualType) -> Visual: ...

    def get_bits_per_rgb(self) -> builtins.int: ...

    def get_blue_pixel_details(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...

    def get_byte_order(self) -> ByteOrder: ...

    def get_colormap_size(self) -> builtins.int: ...

    def get_depth(self) -> builtins.int: ...

    def get_green_pixel_details(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...

    def get_red_pixel_details(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...

    def get_screen(self) -> Screen: ...

    @staticmethod
    def get_system() -> Visual: ...

    def get_visual_type(self) -> VisualType: ...


class Window(GObject.Object):

    @staticmethod
    def at_pointer() -> typing.Tuple[Window, builtins.int, builtins.int]: ...

    def beep(self) -> None: ...

    def begin_draw_frame(self, region: cairo.Region) -> DrawingContext: ...

    def begin_move_drag(self, button: builtins.int, root_x: builtins.int, root_y: builtins.int, timestamp: builtins.int) -> None: ...

    def begin_move_drag_for_device(self, device: Device, button: builtins.int, root_x: builtins.int, root_y: builtins.int, timestamp: builtins.int) -> None: ...

    def begin_paint_rect(self, rectangle: Rectangle) -> None: ...

    def begin_paint_region(self, region: cairo.Region) -> None: ...

    def begin_resize_drag(self, edge: WindowEdge, button: builtins.int, root_x: builtins.int, root_y: builtins.int, timestamp: builtins.int) -> None: ...

    def begin_resize_drag_for_device(self, edge: WindowEdge, device: Device, button: builtins.int, root_x: builtins.int, root_y: builtins.int, timestamp: builtins.int) -> None: ...

    def configure_finished(self) -> None: ...

    @staticmethod
    def constrain_size(geometry: Geometry, flags: WindowHints, width: builtins.int, height: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...

    def coords_from_parent(self, parent_x: builtins.float, parent_y: builtins.float) -> typing.Tuple[builtins.float, builtins.float]: ...

    def coords_to_parent(self, x: builtins.float, y: builtins.float) -> typing.Tuple[builtins.float, builtins.float]: ...

    def create_gl_context(self) -> GLContext: ...

    def create_similar_image_surface(self, format: builtins.int, width: builtins.int, height: builtins.int, scale: builtins.int) -> cairo.Surface: ...

    def create_similar_surface(self, content: cairo.Content, width: builtins.int, height: builtins.int) -> cairo.Surface: ...

    def deiconify(self) -> None: ...

    def destroy(self) -> None: ...

    def destroy_notify(self) -> None: ...

    def enable_synchronized_configure(self) -> None: ...

    def end_draw_frame(self, context: DrawingContext) -> None: ...

    def end_paint(self) -> None: ...

    def ensure_native(self) -> builtins.bool: ...

    def flush(self) -> None: ...

    def focus(self, timestamp: builtins.int) -> None: ...

    def freeze_toplevel_updates_libgtk_only(self) -> None: ...

    def freeze_updates(self) -> None: ...

    def fullscreen(self) -> None: ...

    def fullscreen_on_monitor(self, monitor: builtins.int) -> None: ...

    def geometry_changed(self) -> None: ...

    def get_accept_focus(self) -> builtins.bool: ...

    def get_background_pattern(self) -> typing.Optional[cairo.Pattern]: ...

    def get_children(self) -> typing.Sequence[Window]: ...

    def get_children_with_user_data(self, user_data: typing.Optional[builtins.object]) -> typing.Sequence[Window]: ...

    def get_clip_region(self) -> cairo.Region: ...

    def get_composited(self) -> builtins.bool: ...

    def get_cursor(self) -> typing.Optional[Cursor]: ...

    def get_decorations(self) -> typing.Tuple[builtins.bool, WMDecoration]: ...

    def get_device_cursor(self, device: Device) -> typing.Optional[Cursor]: ...

    def get_device_events(self, device: Device) -> EventMask: ...

    def get_device_position(self, device: Device) -> typing.Tuple[typing.Optional[Window], builtins.int, builtins.int, ModifierType]: ...

    def get_device_position_double(self, device: Device) -> typing.Tuple[typing.Optional[Window], builtins.float, builtins.float, ModifierType]: ...

    def get_display(self) -> Display: ...

    def get_drag_protocol(self) -> typing.Tuple[DragProtocol, Window]: ...

    def get_effective_parent(self) -> Window: ...

    def get_effective_toplevel(self) -> Window: ...

    def get_event_compression(self) -> builtins.bool: ...

    def get_events(self) -> EventMask: ...

    def get_focus_on_map(self) -> builtins.bool: ...

    def get_frame_clock(self) -> FrameClock: ...

    def get_frame_extents(self) -> Rectangle: ...

    def get_fullscreen_mode(self) -> FullscreenMode: ...

    def get_geometry(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int, builtins.int]: ...

    def get_group(self) -> Window: ...

    def get_height(self) -> builtins.int: ...

    def get_modal_hint(self) -> builtins.bool: ...

    def get_origin(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...

    def get_parent(self) -> Window: ...

    def get_pass_through(self) -> builtins.bool: ...

    def get_pointer(self) -> typing.Tuple[typing.Optional[Window], builtins.int, builtins.int, ModifierType]: ...

    def get_position(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_root_coords(self, x: builtins.int, y: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_root_origin(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_scale_factor(self) -> builtins.int: ...

    def get_screen(self) -> Screen: ...

    def get_source_events(self, source: InputSource) -> EventMask: ...

    def get_state(self) -> WindowState: ...

    def get_support_multidevice(self) -> builtins.bool: ...

    def get_toplevel(self) -> Window: ...

    def get_type_hint(self) -> WindowTypeHint: ...

    def get_update_area(self) -> cairo.Region: ...

    def get_user_data(self) -> builtins.object: ...

    def get_visible_region(self) -> cairo.Region: ...

    def get_visual(self) -> Visual: ...

    def get_width(self) -> builtins.int: ...

    def get_window_type(self) -> WindowType: ...

    def has_native(self) -> builtins.bool: ...

    def hide(self) -> None: ...

    def iconify(self) -> None: ...

    def input_shape_combine_region(self, shape_region: cairo.Region, offset_x: builtins.int, offset_y: builtins.int) -> None: ...

    def invalidate_maybe_recurse(self, region: cairo.Region, child_func: typing.Optional[WindowChildFunc], *user_data: typing.Optional[builtins.object]) -> None: ...

    def invalidate_rect(self, rect: typing.Optional[Rectangle], invalidate_children: builtins.bool) -> None: ...

    def invalidate_region(self, region: cairo.Region, invalidate_children: builtins.bool) -> None: ...

    def is_destroyed(self) -> builtins.bool: ...

    def is_input_only(self) -> builtins.bool: ...

    def is_shaped(self) -> builtins.bool: ...

    def is_viewable(self) -> builtins.bool: ...

    def is_visible(self) -> builtins.bool: ...

    def lower(self) -> None: ...

    def mark_paint_from_clip(self, cr: cairo.Context) -> None: ...

    def maximize(self) -> None: ...

    def merge_child_input_shapes(self) -> None: ...

    def merge_child_shapes(self) -> None: ...

    def move(self, x: builtins.int, y: builtins.int) -> None: ...

    def move_region(self, region: cairo.Region, dx: builtins.int, dy: builtins.int) -> None: ...

    def move_resize(self, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...

    def move_to_rect(self, rect: Rectangle, rect_anchor: Gravity, window_anchor: Gravity, anchor_hints: AnchorHints, rect_anchor_dx: builtins.int, rect_anchor_dy: builtins.int) -> None: ...

    @staticmethod
    def new(parent: typing.Optional[Window], attributes: WindowAttr, attributes_mask: WindowAttributesType, **kwargs) -> Window: ...  # type: ignore

    def peek_children(self) -> typing.Sequence[Window]: ...

    @staticmethod
    def process_all_updates() -> None: ...

    def process_updates(self, update_children: builtins.bool) -> None: ...

    def raise_(self) -> None: ...

    def register_dnd(self) -> None: ...

    def reparent(self, new_parent: Window, x: builtins.int, y: builtins.int) -> None: ...

    def resize(self, width: builtins.int, height: builtins.int) -> None: ...

    def restack(self, sibling: typing.Optional[Window], above: builtins.bool) -> None: ...

    def scroll(self, dx: builtins.int, dy: builtins.int) -> None: ...

    def set_accept_focus(self, accept_focus: builtins.bool) -> None: ...

    def set_background(self, color: Color) -> None: ...

    def set_background_pattern(self, pattern: typing.Optional[cairo.Pattern]) -> None: ...

    def set_background_rgba(self, rgba: RGBA) -> None: ...

    def set_child_input_shapes(self) -> None: ...

    def set_child_shapes(self) -> None: ...

    def set_composited(self, composited: builtins.bool) -> None: ...

    def set_cursor(self, cursor: typing.Optional[Cursor]) -> None: ...

    @staticmethod
    def set_debug_updates(setting: builtins.bool) -> None: ...

    def set_decorations(self, decorations: WMDecoration) -> None: ...

    def set_device_cursor(self, device: Device, cursor: Cursor) -> None: ...

    def set_device_events(self, device: Device, event_mask: EventMask) -> None: ...

    def set_event_compression(self, event_compression: builtins.bool) -> None: ...

    def set_events(self, event_mask: EventMask) -> None: ...

    def set_focus_on_map(self, focus_on_map: builtins.bool) -> None: ...

    def set_fullscreen_mode(self, mode: FullscreenMode) -> None: ...

    def set_functions(self, functions: WMFunction) -> None: ...

    def set_geometry_hints(self, geometry: Geometry, geom_mask: WindowHints) -> None: ...

    def set_group(self, leader: typing.Optional[Window]) -> None: ...

    def set_icon_list(self, pixbufs: typing.Sequence[GdkPixbuf.Pixbuf]) -> None: ...

    def set_icon_name(self, name: typing.Optional[builtins.str]) -> None: ...

    def set_keep_above(self, setting: builtins.bool) -> None: ...

    def set_keep_below(self, setting: builtins.bool) -> None: ...

    def set_modal_hint(self, modal: builtins.bool) -> None: ...

    def set_opacity(self, opacity: builtins.float) -> None: ...

    def set_opaque_region(self, region: typing.Optional[cairo.Region]) -> None: ...

    def set_override_redirect(self, override_redirect: builtins.bool) -> None: ...

    def set_pass_through(self, pass_through: builtins.bool) -> None: ...

    def set_role(self, role: builtins.str) -> None: ...

    def set_shadow_width(self, left: builtins.int, right: builtins.int, top: builtins.int, bottom: builtins.int) -> None: ...

    def set_skip_pager_hint(self, skips_pager: builtins.bool) -> None: ...

    def set_skip_taskbar_hint(self, skips_taskbar: builtins.bool) -> None: ...

    def set_source_events(self, source: InputSource, event_mask: EventMask) -> None: ...

    def set_startup_id(self, startup_id: builtins.str) -> None: ...

    def set_static_gravities(self, use_static: builtins.bool) -> builtins.bool: ...

    def set_support_multidevice(self, support_multidevice: builtins.bool) -> None: ...

    def set_title(self, title: builtins.str) -> None: ...

    def set_transient_for(self, parent: Window) -> None: ...

    def set_type_hint(self, hint: WindowTypeHint) -> None: ...

    def set_urgency_hint(self, urgent: builtins.bool) -> None: ...

    def set_user_data(self, user_data: typing.Optional[GObject.Object]) -> None: ...

    def shape_combine_region(self, shape_region: typing.Optional[cairo.Region], offset_x: builtins.int, offset_y: builtins.int) -> None: ...

    def show(self) -> None: ...

    def show_unraised(self) -> None: ...

    def show_window_menu(self, event: Event) -> builtins.bool: ...

    def stick(self) -> None: ...

    def thaw_toplevel_updates_libgtk_only(self) -> None: ...

    def thaw_updates(self) -> None: ...

    def unfullscreen(self) -> None: ...

    def unmaximize(self) -> None: ...

    def unstick(self) -> None: ...

    def withdraw(self) -> None: ...

    def do_create_surface(self, width: builtins.int, height: builtins.int) -> cairo.Surface: ...

    def do_from_embedder(self, embedder_x: builtins.float, embedder_y: builtins.float, offscreen_x: builtins.float, offscreen_y: builtins.float) -> None: ...

    def do_to_embedder(self, offscreen_x: builtins.float, offscreen_y: builtins.float, embedder_x: builtins.float, embedder_y: builtins.float) -> None: ...


class Atom():

    @staticmethod
    def intern(atom_name: builtins.str, only_if_exists: builtins.bool) -> Atom: ...

    @staticmethod
    def intern_static_string(atom_name: builtins.str) -> Atom: ...

    def name(self) -> builtins.str: ...


class Color():
    blue: builtins.int
    green: builtins.int
    pixel: builtins.int
    red: builtins.int

    def copy(self) -> Color: ...

    def equal(self, colorb: Color) -> builtins.bool: ...

    def free(self) -> None: ...

    def hash(self) -> builtins.int: ...

    @staticmethod
    def parse(spec: builtins.str) -> typing.Tuple[builtins.bool, Color]: ...

    def to_string(self) -> builtins.str: ...


class EventAny():
    send_event: builtins.int
    type: EventType
    window: Window


class EventButton():
    axes: builtins.float
    button: builtins.int
    device: Device
    send_event: builtins.int
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventConfigure():
    height: builtins.int
    send_event: builtins.int
    type: EventType
    width: builtins.int
    window: Window
    x: builtins.int
    y: builtins.int


class EventCrossing():
    detail: NotifyType
    focus: builtins.bool
    mode: CrossingMode
    send_event: builtins.int
    state: ModifierType
    subwindow: Window
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventDND():
    context: DragContext
    send_event: builtins.int
    time: builtins.int
    type: EventType
    window: Window
    x_root: builtins.int
    y_root: builtins.int


class EventExpose():
    area: Rectangle
    count: builtins.int
    region: cairo.Region
    send_event: builtins.int
    type: EventType
    window: Window


class EventFocus():
    in_: builtins.int
    send_event: builtins.int
    type: EventType
    window: Window


class EventGrabBroken():
    grab_window: Window
    implicit: builtins.bool
    keyboard: builtins.bool
    send_event: builtins.int
    type: EventType
    window: Window


class EventKey():
    group: builtins.int
    hardware_keycode: builtins.int
    is_modifier: builtins.int
    keyval: builtins.int
    length: builtins.int
    send_event: builtins.int
    state: ModifierType
    string: builtins.str
    time: builtins.int
    type: EventType
    window: Window


class EventMotion():
    axes: builtins.float
    device: Device
    is_hint: builtins.int
    send_event: builtins.int
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventOwnerChange():
    owner: Window
    reason: OwnerChange
    selection: Atom
    selection_time: builtins.int
    send_event: builtins.int
    time: builtins.int
    type: EventType
    window: Window


class EventPadAxis():
    group: builtins.int
    index: builtins.int
    mode: builtins.int
    send_event: builtins.int
    time: builtins.int
    type: EventType
    value: builtins.float
    window: Window


class EventPadButton():
    button: builtins.int
    group: builtins.int
    mode: builtins.int
    send_event: builtins.int
    time: builtins.int
    type: EventType
    window: Window


class EventPadGroupMode():
    group: builtins.int
    mode: builtins.int
    send_event: builtins.int
    time: builtins.int
    type: EventType
    window: Window


class EventProperty():
    atom: Atom
    send_event: builtins.int
    state: PropertyState
    time: builtins.int
    type: EventType
    window: Window


class EventProximity():
    device: Device
    send_event: builtins.int
    time: builtins.int
    type: EventType
    window: Window


class EventScroll():
    delta_x: builtins.float
    delta_y: builtins.float
    device: Device
    direction: ScrollDirection
    is_stop: builtins.int
    send_event: builtins.int
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventSelection():
    property: Atom
    requestor: Window
    selection: Atom
    send_event: builtins.int
    target: Atom
    time: builtins.int
    type: EventType
    window: Window


class EventSequence():
    ...


class EventSetting():
    action: SettingAction
    name: builtins.str
    send_event: builtins.int
    type: EventType
    window: Window


class EventTouch():
    axes: builtins.float
    device: Device
    emulating_pointer: builtins.bool
    send_event: builtins.int
    sequence: EventSequence
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventTouchpadPinch():
    angle_delta: builtins.float
    dx: builtins.float
    dy: builtins.float
    n_fingers: builtins.int
    phase: builtins.int
    scale: builtins.float
    send_event: builtins.int
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventTouchpadSwipe():
    dx: builtins.float
    dy: builtins.float
    n_fingers: builtins.int
    phase: builtins.int
    send_event: builtins.int
    state: ModifierType
    time: builtins.int
    type: EventType
    window: Window
    x: builtins.float
    x_root: builtins.float
    y: builtins.float
    y_root: builtins.float


class EventVisibility():
    send_event: builtins.int
    state: VisibilityState
    type: EventType
    window: Window


class EventWindowState():
    changed_mask: WindowState
    new_window_state: WindowState
    send_event: builtins.int
    type: EventType
    window: Window


class FrameTimings():

    def get_complete(self) -> builtins.bool: ...

    def get_frame_counter(self) -> builtins.int: ...

    def get_frame_time(self) -> builtins.int: ...

    def get_predicted_presentation_time(self) -> builtins.int: ...

    def get_presentation_time(self) -> builtins.int: ...

    def get_refresh_interval(self) -> builtins.int: ...

    def ref(self) -> FrameTimings: ...

    def unref(self) -> None: ...


class Geometry():
    base_height: builtins.int
    base_width: builtins.int
    height_inc: builtins.int
    max_aspect: builtins.float
    max_height: builtins.int
    max_width: builtins.int
    min_aspect: builtins.float
    min_height: builtins.int
    min_width: builtins.int
    width_inc: builtins.int
    win_gravity: Gravity


class KeymapKey():
    group: builtins.int
    keycode: builtins.int
    level: builtins.int


class Point():
    x: builtins.int
    y: builtins.int


class RGBA():
    alpha: builtins.float
    blue: builtins.float
    green: builtins.float
    red: builtins.float

    def __init__(self, red: float = 1.0, green: float = 1.0, blue: float = 1.0, alpha: float = 1.0) -> None: ...

    def copy(self) -> RGBA: ...

    def equal(self, p2: RGBA) -> builtins.bool: ...

    def free(self) -> None: ...

    def hash(self) -> builtins.int: ...

    def parse(self, spec: builtins.str) -> builtins.bool: ...

    def to_string(self) -> builtins.str: ...


class Rectangle():
    height: builtins.int
    width: builtins.int
    x: builtins.int
    y: builtins.int

    def equal(self, rect2: Rectangle) -> builtins.bool: ...

    def intersect(self, src2: Rectangle) -> typing.Tuple[builtins.bool, Rectangle]: ...

    def union(self, src2: Rectangle) -> Rectangle: ...


class TimeCoord():
    axes: typing.Sequence[builtins.float]
    time: builtins.int


class WindowAttr():
    cursor: Cursor
    event_mask: builtins.int
    height: builtins.int
    override_redirect: builtins.bool
    title: builtins.str
    type_hint: WindowTypeHint
    visual: Visual
    wclass: WindowWindowClass
    width: builtins.int
    window_type: WindowType
    wmclass_class: builtins.str
    wmclass_name: builtins.str
    x: builtins.int
    y: builtins.int


class WindowRedirect():
    ...


class Event():
    any: EventAny
    button: EventButton
    configure: EventConfigure
    crossing: EventCrossing
    dnd: EventDND
    expose: EventExpose
    focus_change: EventFocus
    grab_broken: EventGrabBroken
    key: EventKey
    motion: EventMotion
    owner_change: EventOwnerChange
    pad_axis: EventPadAxis
    pad_button: EventPadButton
    pad_group_mode: EventPadGroupMode
    property: EventProperty
    proximity: EventProximity
    scroll: EventScroll
    selection: EventSelection
    setting: EventSetting
    touch: EventTouch
    touchpad_pinch: EventTouchpadPinch
    touchpad_swipe: EventTouchpadSwipe
    type: EventType
    visibility: EventVisibility
    window_state: EventWindowState

    def copy(self) -> Event: ...

    def free(self) -> None: ...

    @staticmethod
    def get() -> typing.Optional[Event]: ...

    def get_axis(self, axis_use: AxisUse) -> typing.Tuple[builtins.bool, builtins.float]: ...

    def get_button(self) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def get_click_count(self) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def get_coords(self) -> typing.Tuple[builtins.bool, builtins.float, builtins.float]: ...

    def get_device(self) -> typing.Optional[Device]: ...

    def get_device_tool(self) -> DeviceTool: ...

    def get_event_sequence(self) -> EventSequence: ...

    def get_event_type(self) -> EventType: ...

    def get_keycode(self) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def get_keyval(self) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def get_pointer_emulated(self) -> builtins.bool: ...

    def get_root_coords(self) -> typing.Tuple[builtins.bool, builtins.float, builtins.float]: ...

    def get_scancode(self) -> builtins.int: ...

    def get_screen(self) -> Screen: ...

    def get_scroll_deltas(self) -> typing.Tuple[builtins.bool, builtins.float, builtins.float]: ...

    def get_scroll_direction(self) -> typing.Tuple[builtins.bool, ScrollDirection]: ...

    def get_seat(self) -> Seat: ...

    def get_source_device(self) -> typing.Optional[Device]: ...

    def get_state(self) -> typing.Tuple[builtins.bool, ModifierType]: ...

    def get_time(self) -> builtins.int: ...

    def get_window(self) -> Window: ...

    @staticmethod
    def handler_set(func: EventFunc, *data: typing.Optional[builtins.object]) -> None: ...

    def is_scroll_stop_event(self) -> builtins.bool: ...

    @staticmethod
    def new(type: EventType) -> Event: ...

    @staticmethod
    def peek() -> typing.Optional[Event]: ...

    def put(self) -> None: ...

    @staticmethod
    def request_motions(event: EventMotion) -> None: ...

    def set_device(self, device: Device) -> None: ...

    def set_device_tool(self, tool: typing.Optional[DeviceTool]) -> None: ...

    def set_screen(self, screen: Screen) -> None: ...

    def set_source_device(self, device: Device) -> None: ...

    def triggers_context_menu(self) -> builtins.bool: ...


class AnchorHints(GObject.GFlags, builtins.int):
    FLIP = ...  # type: AnchorHints
    FLIP_X = ...  # type: AnchorHints
    FLIP_Y = ...  # type: AnchorHints
    RESIZE = ...  # type: AnchorHints
    RESIZE_X = ...  # type: AnchorHints
    RESIZE_Y = ...  # type: AnchorHints
    SLIDE = ...  # type: AnchorHints
    SLIDE_X = ...  # type: AnchorHints
    SLIDE_Y = ...  # type: AnchorHints


class AxisFlags(GObject.GFlags, builtins.int):
    DISTANCE = ...  # type: AxisFlags
    PRESSURE = ...  # type: AxisFlags
    ROTATION = ...  # type: AxisFlags
    SLIDER = ...  # type: AxisFlags
    WHEEL = ...  # type: AxisFlags
    X = ...  # type: AxisFlags
    XTILT = ...  # type: AxisFlags
    Y = ...  # type: AxisFlags
    YTILT = ...  # type: AxisFlags


class DragAction(GObject.GFlags, builtins.int):
    ASK = ...  # type: DragAction
    COPY = ...  # type: DragAction
    DEFAULT = ...  # type: DragAction
    LINK = ...  # type: DragAction
    MOVE = ...  # type: DragAction
    PRIVATE = ...  # type: DragAction


class EventMask(GObject.GFlags, builtins.int):
    ALL_EVENTS_MASK = ...  # type: EventMask
    BUTTON1_MOTION_MASK = ...  # type: EventMask
    BUTTON2_MOTION_MASK = ...  # type: EventMask
    BUTTON3_MOTION_MASK = ...  # type: EventMask
    BUTTON_MOTION_MASK = ...  # type: EventMask
    BUTTON_PRESS_MASK = ...  # type: EventMask
    BUTTON_RELEASE_MASK = ...  # type: EventMask
    ENTER_NOTIFY_MASK = ...  # type: EventMask
    EXPOSURE_MASK = ...  # type: EventMask
    FOCUS_CHANGE_MASK = ...  # type: EventMask
    KEY_PRESS_MASK = ...  # type: EventMask
    KEY_RELEASE_MASK = ...  # type: EventMask
    LEAVE_NOTIFY_MASK = ...  # type: EventMask
    POINTER_MOTION_HINT_MASK = ...  # type: EventMask
    POINTER_MOTION_MASK = ...  # type: EventMask
    PROPERTY_CHANGE_MASK = ...  # type: EventMask
    PROXIMITY_IN_MASK = ...  # type: EventMask
    PROXIMITY_OUT_MASK = ...  # type: EventMask
    SCROLL_MASK = ...  # type: EventMask
    SMOOTH_SCROLL_MASK = ...  # type: EventMask
    STRUCTURE_MASK = ...  # type: EventMask
    SUBSTRUCTURE_MASK = ...  # type: EventMask
    TABLET_PAD_MASK = ...  # type: EventMask
    TOUCHPAD_GESTURE_MASK = ...  # type: EventMask
    TOUCH_MASK = ...  # type: EventMask
    VISIBILITY_NOTIFY_MASK = ...  # type: EventMask


class FrameClockPhase(GObject.GFlags, builtins.int):
    AFTER_PAINT = ...  # type: FrameClockPhase
    BEFORE_PAINT = ...  # type: FrameClockPhase
    FLUSH_EVENTS = ...  # type: FrameClockPhase
    LAYOUT = ...  # type: FrameClockPhase
    NONE = ...  # type: FrameClockPhase
    PAINT = ...  # type: FrameClockPhase
    RESUME_EVENTS = ...  # type: FrameClockPhase
    UPDATE = ...  # type: FrameClockPhase


class ModifierType(GObject.GFlags, builtins.int):
    BUTTON1_MASK = ...  # type: ModifierType
    BUTTON2_MASK = ...  # type: ModifierType
    BUTTON3_MASK = ...  # type: ModifierType
    BUTTON4_MASK = ...  # type: ModifierType
    BUTTON5_MASK = ...  # type: ModifierType
    CONTROL_MASK = ...  # type: ModifierType
    HYPER_MASK = ...  # type: ModifierType
    LOCK_MASK = ...  # type: ModifierType
    META_MASK = ...  # type: ModifierType
    MOD1_MASK = ...  # type: ModifierType
    MOD2_MASK = ...  # type: ModifierType
    MOD3_MASK = ...  # type: ModifierType
    MOD4_MASK = ...  # type: ModifierType
    MOD5_MASK = ...  # type: ModifierType
    MODIFIER_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_13_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_14_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_15_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_16_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_17_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_18_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_19_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_20_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_21_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_22_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_23_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_24_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_25_MASK = ...  # type: ModifierType
    MODIFIER_RESERVED_29_MASK = ...  # type: ModifierType
    RELEASE_MASK = ...  # type: ModifierType
    SHIFT_MASK = ...  # type: ModifierType
    SUPER_MASK = ...  # type: ModifierType


class SeatCapabilities(GObject.GFlags, builtins.int):
    ALL = ...  # type: SeatCapabilities
    ALL_POINTING = ...  # type: SeatCapabilities
    KEYBOARD = ...  # type: SeatCapabilities
    NONE = ...  # type: SeatCapabilities
    POINTER = ...  # type: SeatCapabilities
    TABLET_STYLUS = ...  # type: SeatCapabilities
    TOUCH = ...  # type: SeatCapabilities


class WMDecoration(GObject.GFlags, builtins.int):
    ALL = ...  # type: WMDecoration
    BORDER = ...  # type: WMDecoration
    MAXIMIZE = ...  # type: WMDecoration
    MENU = ...  # type: WMDecoration
    MINIMIZE = ...  # type: WMDecoration
    RESIZEH = ...  # type: WMDecoration
    TITLE = ...  # type: WMDecoration


class WMFunction(GObject.GFlags, builtins.int):
    ALL = ...  # type: WMFunction
    CLOSE = ...  # type: WMFunction
    MAXIMIZE = ...  # type: WMFunction
    MINIMIZE = ...  # type: WMFunction
    MOVE = ...  # type: WMFunction
    RESIZE = ...  # type: WMFunction


class WindowAttributesType(GObject.GFlags, builtins.int):
    CURSOR = ...  # type: WindowAttributesType
    NOREDIR = ...  # type: WindowAttributesType
    TITLE = ...  # type: WindowAttributesType
    TYPE_HINT = ...  # type: WindowAttributesType
    VISUAL = ...  # type: WindowAttributesType
    WMCLASS = ...  # type: WindowAttributesType
    X = ...  # type: WindowAttributesType
    Y = ...  # type: WindowAttributesType


class WindowHints(GObject.GFlags, builtins.int):
    ASPECT = ...  # type: WindowHints
    BASE_SIZE = ...  # type: WindowHints
    MAX_SIZE = ...  # type: WindowHints
    MIN_SIZE = ...  # type: WindowHints
    POS = ...  # type: WindowHints
    RESIZE_INC = ...  # type: WindowHints
    USER_POS = ...  # type: WindowHints
    USER_SIZE = ...  # type: WindowHints
    WIN_GRAVITY = ...  # type: WindowHints


class WindowState(GObject.GFlags, builtins.int):
    ABOVE = ...  # type: WindowState
    BELOW = ...  # type: WindowState
    BOTTOM_RESIZABLE = ...  # type: WindowState
    BOTTOM_TILED = ...  # type: WindowState
    FOCUSED = ...  # type: WindowState
    FULLSCREEN = ...  # type: WindowState
    ICONIFIED = ...  # type: WindowState
    LEFT_RESIZABLE = ...  # type: WindowState
    LEFT_TILED = ...  # type: WindowState
    MAXIMIZED = ...  # type: WindowState
    RIGHT_RESIZABLE = ...  # type: WindowState
    RIGHT_TILED = ...  # type: WindowState
    STICKY = ...  # type: WindowState
    TILED = ...  # type: WindowState
    TOP_RESIZABLE = ...  # type: WindowState
    TOP_TILED = ...  # type: WindowState
    WITHDRAWN = ...  # type: WindowState


class AxisUse(GObject.GEnum, builtins.int):
    DISTANCE = ...  # type: AxisUse
    IGNORE = ...  # type: AxisUse
    LAST = ...  # type: AxisUse
    PRESSURE = ...  # type: AxisUse
    ROTATION = ...  # type: AxisUse
    SLIDER = ...  # type: AxisUse
    WHEEL = ...  # type: AxisUse
    X = ...  # type: AxisUse
    XTILT = ...  # type: AxisUse
    Y = ...  # type: AxisUse
    YTILT = ...  # type: AxisUse


class ByteOrder(GObject.GEnum, builtins.int):
    LSB_FIRST = ...  # type: ByteOrder
    MSB_FIRST = ...  # type: ByteOrder


class CrossingMode(GObject.GEnum, builtins.int):
    DEVICE_SWITCH = ...  # type: CrossingMode
    GRAB = ...  # type: CrossingMode
    GTK_GRAB = ...  # type: CrossingMode
    GTK_UNGRAB = ...  # type: CrossingMode
    NORMAL = ...  # type: CrossingMode
    STATE_CHANGED = ...  # type: CrossingMode
    TOUCH_BEGIN = ...  # type: CrossingMode
    TOUCH_END = ...  # type: CrossingMode
    UNGRAB = ...  # type: CrossingMode


class CursorType(GObject.GEnum, builtins.int):
    ARROW = ...  # type: CursorType
    BASED_ARROW_DOWN = ...  # type: CursorType
    BASED_ARROW_UP = ...  # type: CursorType
    BLANK_CURSOR = ...  # type: CursorType
    BOAT = ...  # type: CursorType
    BOGOSITY = ...  # type: CursorType
    BOTTOM_LEFT_CORNER = ...  # type: CursorType
    BOTTOM_RIGHT_CORNER = ...  # type: CursorType
    BOTTOM_SIDE = ...  # type: CursorType
    BOTTOM_TEE = ...  # type: CursorType
    BOX_SPIRAL = ...  # type: CursorType
    CENTER_PTR = ...  # type: CursorType
    CIRCLE = ...  # type: CursorType
    CLOCK = ...  # type: CursorType
    COFFEE_MUG = ...  # type: CursorType
    CROSS = ...  # type: CursorType
    CROSSHAIR = ...  # type: CursorType
    CROSS_REVERSE = ...  # type: CursorType
    CURSOR_IS_PIXMAP = ...  # type: CursorType
    DIAMOND_CROSS = ...  # type: CursorType
    DOT = ...  # type: CursorType
    DOTBOX = ...  # type: CursorType
    DOUBLE_ARROW = ...  # type: CursorType
    DRAFT_LARGE = ...  # type: CursorType
    DRAFT_SMALL = ...  # type: CursorType
    DRAPED_BOX = ...  # type: CursorType
    EXCHANGE = ...  # type: CursorType
    FLEUR = ...  # type: CursorType
    GOBBLER = ...  # type: CursorType
    GUMBY = ...  # type: CursorType
    HAND1 = ...  # type: CursorType
    HAND2 = ...  # type: CursorType
    HEART = ...  # type: CursorType
    ICON = ...  # type: CursorType
    IRON_CROSS = ...  # type: CursorType
    LAST_CURSOR = ...  # type: CursorType
    LEFTBUTTON = ...  # type: CursorType
    LEFT_PTR = ...  # type: CursorType
    LEFT_SIDE = ...  # type: CursorType
    LEFT_TEE = ...  # type: CursorType
    LL_ANGLE = ...  # type: CursorType
    LR_ANGLE = ...  # type: CursorType
    MAN = ...  # type: CursorType
    MIDDLEBUTTON = ...  # type: CursorType
    MOUSE = ...  # type: CursorType
    PENCIL = ...  # type: CursorType
    PIRATE = ...  # type: CursorType
    PLUS = ...  # type: CursorType
    QUESTION_ARROW = ...  # type: CursorType
    RIGHTBUTTON = ...  # type: CursorType
    RIGHT_PTR = ...  # type: CursorType
    RIGHT_SIDE = ...  # type: CursorType
    RIGHT_TEE = ...  # type: CursorType
    RTL_LOGO = ...  # type: CursorType
    SAILBOAT = ...  # type: CursorType
    SB_DOWN_ARROW = ...  # type: CursorType
    SB_H_DOUBLE_ARROW = ...  # type: CursorType
    SB_LEFT_ARROW = ...  # type: CursorType
    SB_RIGHT_ARROW = ...  # type: CursorType
    SB_UP_ARROW = ...  # type: CursorType
    SB_V_DOUBLE_ARROW = ...  # type: CursorType
    SHUTTLE = ...  # type: CursorType
    SIZING = ...  # type: CursorType
    SPIDER = ...  # type: CursorType
    SPRAYCAN = ...  # type: CursorType
    STAR = ...  # type: CursorType
    TARGET = ...  # type: CursorType
    TCROSS = ...  # type: CursorType
    TOP_LEFT_ARROW = ...  # type: CursorType
    TOP_LEFT_CORNER = ...  # type: CursorType
    TOP_RIGHT_CORNER = ...  # type: CursorType
    TOP_SIDE = ...  # type: CursorType
    TOP_TEE = ...  # type: CursorType
    TREK = ...  # type: CursorType
    UL_ANGLE = ...  # type: CursorType
    UMBRELLA = ...  # type: CursorType
    UR_ANGLE = ...  # type: CursorType
    WATCH = ...  # type: CursorType
    XTERM = ...  # type: CursorType
    X_CURSOR = ...  # type: CursorType


class DevicePadFeature(GObject.GEnum, builtins.int):
    BUTTON = ...  # type: DevicePadFeature
    RING = ...  # type: DevicePadFeature
    STRIP = ...  # type: DevicePadFeature


class DeviceToolType(GObject.GEnum, builtins.int):
    AIRBRUSH = ...  # type: DeviceToolType
    BRUSH = ...  # type: DeviceToolType
    ERASER = ...  # type: DeviceToolType
    LENS = ...  # type: DeviceToolType
    MOUSE = ...  # type: DeviceToolType
    PEN = ...  # type: DeviceToolType
    PENCIL = ...  # type: DeviceToolType
    UNKNOWN = ...  # type: DeviceToolType


class DeviceType(GObject.GEnum, builtins.int):
    FLOATING = ...  # type: DeviceType
    MASTER = ...  # type: DeviceType
    SLAVE = ...  # type: DeviceType


class DragCancelReason(GObject.GEnum, builtins.int):
    ERROR = ...  # type: DragCancelReason
    NO_TARGET = ...  # type: DragCancelReason
    USER_CANCELLED = ...  # type: DragCancelReason


class DragProtocol(GObject.GEnum, builtins.int):
    LOCAL = ...  # type: DragProtocol
    MOTIF = ...  # type: DragProtocol
    NONE = ...  # type: DragProtocol
    OLE2 = ...  # type: DragProtocol
    ROOTWIN = ...  # type: DragProtocol
    WAYLAND = ...  # type: DragProtocol
    WIN32_DROPFILES = ...  # type: DragProtocol
    XDND = ...  # type: DragProtocol


class EventType(GObject.GEnum, builtins.int):
    BUTTON_PRESS = ...  # type: EventType
    BUTTON_RELEASE = ...  # type: EventType
    CLIENT_EVENT = ...  # type: EventType
    CONFIGURE = ...  # type: EventType
    DAMAGE = ...  # type: EventType
    DELETE = ...  # type: EventType
    DESTROY = ...  # type: EventType
    DOUBLE_BUTTON_PRESS = ...  # type: EventType
    DRAG_ENTER = ...  # type: EventType
    DRAG_LEAVE = ...  # type: EventType
    DRAG_MOTION = ...  # type: EventType
    DRAG_STATUS = ...  # type: EventType
    DROP_FINISHED = ...  # type: EventType
    DROP_START = ...  # type: EventType
    ENTER_NOTIFY = ...  # type: EventType
    EVENT_LAST = ...  # type: EventType
    EXPOSE = ...  # type: EventType
    FOCUS_CHANGE = ...  # type: EventType
    GRAB_BROKEN = ...  # type: EventType
    KEY_PRESS = ...  # type: EventType
    KEY_RELEASE = ...  # type: EventType
    LEAVE_NOTIFY = ...  # type: EventType
    MAP = ...  # type: EventType
    MOTION_NOTIFY = ...  # type: EventType
    NOTHING = ...  # type: EventType
    OWNER_CHANGE = ...  # type: EventType
    PAD_BUTTON_PRESS = ...  # type: EventType
    PAD_BUTTON_RELEASE = ...  # type: EventType
    PAD_GROUP_MODE = ...  # type: EventType
    PAD_RING = ...  # type: EventType
    PAD_STRIP = ...  # type: EventType
    PROPERTY_NOTIFY = ...  # type: EventType
    PROXIMITY_IN = ...  # type: EventType
    PROXIMITY_OUT = ...  # type: EventType
    SCROLL = ...  # type: EventType
    SELECTION_CLEAR = ...  # type: EventType
    SELECTION_NOTIFY = ...  # type: EventType
    SELECTION_REQUEST = ...  # type: EventType
    SETTING = ...  # type: EventType
    TOUCHPAD_PINCH = ...  # type: EventType
    TOUCHPAD_SWIPE = ...  # type: EventType
    TOUCH_BEGIN = ...  # type: EventType
    TOUCH_CANCEL = ...  # type: EventType
    TOUCH_END = ...  # type: EventType
    TOUCH_UPDATE = ...  # type: EventType
    TRIPLE_BUTTON_PRESS = ...  # type: EventType
    UNMAP = ...  # type: EventType
    VISIBILITY_NOTIFY = ...  # type: EventType
    WINDOW_STATE = ...  # type: EventType
    _2BUTTON_PRESS = ...  # type: EventType
    _3BUTTON_PRESS = ...  # type: EventType


class FilterReturn(GObject.GEnum, builtins.int):
    CONTINUE = ...  # type: FilterReturn
    REMOVE = ...  # type: FilterReturn
    TRANSLATE = ...  # type: FilterReturn


class FullscreenMode(GObject.GEnum, builtins.int):
    ALL_MONITORS = ...  # type: FullscreenMode
    CURRENT_MONITOR = ...  # type: FullscreenMode


class GLError(GObject.GEnum, builtins.int):
    NOT_AVAILABLE = ...  # type: GLError
    UNSUPPORTED_FORMAT = ...  # type: GLError
    UNSUPPORTED_PROFILE = ...  # type: GLError

    @staticmethod
    def quark() -> builtins.int: ...


class GrabOwnership(GObject.GEnum, builtins.int):
    APPLICATION = ...  # type: GrabOwnership
    NONE = ...  # type: GrabOwnership
    WINDOW = ...  # type: GrabOwnership


class GrabStatus(GObject.GEnum, builtins.int):
    ALREADY_GRABBED = ...  # type: GrabStatus
    FAILED = ...  # type: GrabStatus
    FROZEN = ...  # type: GrabStatus
    INVALID_TIME = ...  # type: GrabStatus
    NOT_VIEWABLE = ...  # type: GrabStatus
    SUCCESS = ...  # type: GrabStatus


class Gravity(GObject.GEnum, builtins.int):
    CENTER = ...  # type: Gravity
    EAST = ...  # type: Gravity
    NORTH = ...  # type: Gravity
    NORTH_EAST = ...  # type: Gravity
    NORTH_WEST = ...  # type: Gravity
    SOUTH = ...  # type: Gravity
    SOUTH_EAST = ...  # type: Gravity
    SOUTH_WEST = ...  # type: Gravity
    STATIC = ...  # type: Gravity
    WEST = ...  # type: Gravity


class InputMode(GObject.GEnum, builtins.int):
    DISABLED = ...  # type: InputMode
    SCREEN = ...  # type: InputMode
    WINDOW = ...  # type: InputMode


class InputSource(GObject.GEnum, builtins.int):
    CURSOR = ...  # type: InputSource
    ERASER = ...  # type: InputSource
    KEYBOARD = ...  # type: InputSource
    MOUSE = ...  # type: InputSource
    PEN = ...  # type: InputSource
    TABLET_PAD = ...  # type: InputSource
    TOUCHPAD = ...  # type: InputSource
    TOUCHSCREEN = ...  # type: InputSource
    TRACKPOINT = ...  # type: InputSource


class ModifierIntent(GObject.GEnum, builtins.int):
    CONTEXT_MENU = ...  # type: ModifierIntent
    DEFAULT_MOD_MASK = ...  # type: ModifierIntent
    EXTEND_SELECTION = ...  # type: ModifierIntent
    MODIFY_SELECTION = ...  # type: ModifierIntent
    NO_TEXT_INPUT = ...  # type: ModifierIntent
    PRIMARY_ACCELERATOR = ...  # type: ModifierIntent
    SHIFT_GROUP = ...  # type: ModifierIntent


class NotifyType(GObject.GEnum, builtins.int):
    ANCESTOR = ...  # type: NotifyType
    INFERIOR = ...  # type: NotifyType
    NONLINEAR = ...  # type: NotifyType
    NONLINEAR_VIRTUAL = ...  # type: NotifyType
    UNKNOWN = ...  # type: NotifyType
    VIRTUAL = ...  # type: NotifyType


class OwnerChange(GObject.GEnum, builtins.int):
    CLOSE = ...  # type: OwnerChange
    DESTROY = ...  # type: OwnerChange
    NEW_OWNER = ...  # type: OwnerChange


class PropMode(GObject.GEnum, builtins.int):
    APPEND = ...  # type: PropMode
    PREPEND = ...  # type: PropMode
    REPLACE = ...  # type: PropMode


class PropertyState(GObject.GEnum, builtins.int):
    DELETE = ...  # type: PropertyState
    NEW_VALUE = ...  # type: PropertyState


class ScrollDirection(GObject.GEnum, builtins.int):
    DOWN = ...  # type: ScrollDirection
    LEFT = ...  # type: ScrollDirection
    RIGHT = ...  # type: ScrollDirection
    SMOOTH = ...  # type: ScrollDirection
    UP = ...  # type: ScrollDirection


class SettingAction(GObject.GEnum, builtins.int):
    CHANGED = ...  # type: SettingAction
    DELETED = ...  # type: SettingAction
    NEW = ...  # type: SettingAction


class Status(GObject.GEnum, builtins.int):
    ERROR = ...  # type: Status
    ERROR_FILE = ...  # type: Status
    ERROR_MEM = ...  # type: Status
    ERROR_PARAM = ...  # type: Status
    OK = ...  # type: Status


class SubpixelLayout(GObject.GEnum, builtins.int):
    HORIZONTAL_BGR = ...  # type: SubpixelLayout
    HORIZONTAL_RGB = ...  # type: SubpixelLayout
    NONE = ...  # type: SubpixelLayout
    UNKNOWN = ...  # type: SubpixelLayout
    VERTICAL_BGR = ...  # type: SubpixelLayout
    VERTICAL_RGB = ...  # type: SubpixelLayout


class TouchpadGesturePhase(GObject.GEnum, builtins.int):
    BEGIN = ...  # type: TouchpadGesturePhase
    CANCEL = ...  # type: TouchpadGesturePhase
    END = ...  # type: TouchpadGesturePhase
    UPDATE = ...  # type: TouchpadGesturePhase


class VisibilityState(GObject.GEnum, builtins.int):
    FULLY_OBSCURED = ...  # type: VisibilityState
    PARTIAL = ...  # type: VisibilityState
    UNOBSCURED = ...  # type: VisibilityState


class VisualType(GObject.GEnum, builtins.int):
    DIRECT_COLOR = ...  # type: VisualType
    GRAYSCALE = ...  # type: VisualType
    PSEUDO_COLOR = ...  # type: VisualType
    STATIC_COLOR = ...  # type: VisualType
    STATIC_GRAY = ...  # type: VisualType
    TRUE_COLOR = ...  # type: VisualType


class WindowEdge(GObject.GEnum, builtins.int):
    EAST = ...  # type: WindowEdge
    NORTH = ...  # type: WindowEdge
    NORTH_EAST = ...  # type: WindowEdge
    NORTH_WEST = ...  # type: WindowEdge
    SOUTH = ...  # type: WindowEdge
    SOUTH_EAST = ...  # type: WindowEdge
    SOUTH_WEST = ...  # type: WindowEdge
    WEST = ...  # type: WindowEdge


class WindowType(GObject.GEnum, builtins.int):
    CHILD = ...  # type: WindowType
    FOREIGN = ...  # type: WindowType
    OFFSCREEN = ...  # type: WindowType
    ROOT = ...  # type: WindowType
    SUBSURFACE = ...  # type: WindowType
    TEMP = ...  # type: WindowType
    TOPLEVEL = ...  # type: WindowType


class WindowTypeHint(GObject.GEnum, builtins.int):
    COMBO = ...  # type: WindowTypeHint
    DESKTOP = ...  # type: WindowTypeHint
    DIALOG = ...  # type: WindowTypeHint
    DND = ...  # type: WindowTypeHint
    DOCK = ...  # type: WindowTypeHint
    DROPDOWN_MENU = ...  # type: WindowTypeHint
    MENU = ...  # type: WindowTypeHint
    NORMAL = ...  # type: WindowTypeHint
    NOTIFICATION = ...  # type: WindowTypeHint
    POPUP_MENU = ...  # type: WindowTypeHint
    SPLASHSCREEN = ...  # type: WindowTypeHint
    TOOLBAR = ...  # type: WindowTypeHint
    TOOLTIP = ...  # type: WindowTypeHint
    UTILITY = ...  # type: WindowTypeHint


class WindowWindowClass(GObject.GEnum, builtins.int):
    INPUT_ONLY = ...  # type: WindowWindowClass
    INPUT_OUTPUT = ...  # type: WindowWindowClass


EventFunc = typing.Callable[[Event, typing.Optional[builtins.object]], None]
FilterFunc = typing.Callable[[builtins.object, Event, typing.Optional[builtins.object]], FilterReturn]
SeatGrabPrepareFunc = typing.Callable[[Seat, Window, typing.Optional[builtins.object]], None]
WindowChildFunc = typing.Callable[[Window, typing.Optional[builtins.object]], builtins.bool]
WindowInvalidateHandlerFunc = typing.Callable[[Window, cairo.Region], None]


def add_option_entries_libgtk_only(group: GLib.OptionGroup) -> None: ...


def atom_intern(atom_name: builtins.str, only_if_exists: builtins.bool) -> Atom: ...


def atom_intern_static_string(atom_name: builtins.str) -> Atom: ...


def beep() -> None: ...


def cairo_create(window: Window) -> cairo.Context: ...


def cairo_draw_from_gl(cr: cairo.Context, window: Window, source: builtins.int, source_type: builtins.int, buffer_scale: builtins.int, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...


def cairo_get_clip_rectangle(cr: cairo.Context) -> typing.Tuple[builtins.bool, Rectangle]: ...


def cairo_get_drawing_context(cr: cairo.Context) -> typing.Optional[DrawingContext]: ...


def cairo_rectangle(cr: cairo.Context, rectangle: Rectangle) -> None: ...


def cairo_region(cr: cairo.Context, region: cairo.Region) -> None: ...


def cairo_region_create_from_surface(surface: cairo.Surface) -> cairo.Region: ...


def cairo_set_source_color(cr: cairo.Context, color: Color) -> None: ...


def cairo_set_source_pixbuf(cr: cairo.Context, pixbuf: GdkPixbuf.Pixbuf, pixbuf_x: builtins.float, pixbuf_y: builtins.float) -> None: ...


def cairo_set_source_rgba(cr: cairo.Context, rgba: RGBA) -> None: ...


def cairo_set_source_window(cr: cairo.Context, window: Window, x: builtins.float, y: builtins.float) -> None: ...


def cairo_surface_create_from_pixbuf(pixbuf: GdkPixbuf.Pixbuf, scale: builtins.int, for_window: typing.Optional[Window]) -> cairo.Surface: ...


def color_parse(spec: builtins.str) -> typing.Tuple[builtins.bool, Color]: ...


def disable_multidevice() -> None: ...


def drag_abort(context: DragContext, time_: builtins.int) -> None: ...


def drag_begin(window: Window, targets: typing.Sequence[Atom]) -> DragContext: ...


def drag_begin_for_device(window: Window, device: Device, targets: typing.Sequence[Atom]) -> DragContext: ...


def drag_begin_from_point(window: Window, device: Device, targets: typing.Sequence[Atom], x_root: builtins.int, y_root: builtins.int) -> DragContext: ...


def drag_drop(context: DragContext, time_: builtins.int) -> None: ...


def drag_drop_done(context: DragContext, success: builtins.bool) -> None: ...


def drag_drop_succeeded(context: DragContext) -> builtins.bool: ...


def drag_find_window_for_screen(context: DragContext, drag_window: Window, screen: Screen, x_root: builtins.int, y_root: builtins.int) -> typing.Tuple[Window, DragProtocol]: ...


def drag_get_selection(context: DragContext) -> Atom: ...


def drag_motion(context: DragContext, dest_window: Window, protocol: DragProtocol, x_root: builtins.int, y_root: builtins.int, suggested_action: DragAction, possible_actions: DragAction, time_: builtins.int) -> builtins.bool: ...


def drag_status(context: DragContext, action: DragAction, time_: builtins.int) -> None: ...


def drop_finish(context: DragContext, success: builtins.bool, time_: builtins.int) -> None: ...


def drop_reply(context: DragContext, accepted: builtins.bool, time_: builtins.int) -> None: ...


def error_trap_pop() -> builtins.int: ...


def error_trap_pop_ignored() -> None: ...


def error_trap_push() -> None: ...


def event_get() -> typing.Optional[Event]: ...


def event_handler_set(func: EventFunc, *data: typing.Optional[builtins.object]) -> None: ...


def event_peek() -> typing.Optional[Event]: ...


def event_request_motions(event: EventMotion) -> None: ...


def events_get_angle(event1: Event, event2: Event) -> typing.Tuple[builtins.bool, builtins.float]: ...


def events_get_center(event1: Event, event2: Event) -> typing.Tuple[builtins.bool, builtins.float, builtins.float]: ...


def events_get_distance(event1: Event, event2: Event) -> typing.Tuple[builtins.bool, builtins.float]: ...


def events_pending() -> builtins.bool: ...


def flush() -> None: ...


def get_default_root_window() -> Window: ...


def get_display() -> builtins.str: ...


def get_display_arg_name() -> typing.Optional[builtins.str]: ...


def get_program_class() -> builtins.str: ...


def get_show_events() -> builtins.bool: ...


def gl_error_quark() -> builtins.int: ...


def init(argv: typing.Sequence[builtins.str]) -> typing.Sequence[builtins.str]: ...


def init_check(argv: typing.Sequence[builtins.str]) -> typing.Tuple[builtins.bool, typing.Sequence[builtins.str]]: ...


def keyboard_grab(window: Window, owner_events: builtins.bool, time_: builtins.int) -> GrabStatus: ...


def keyboard_ungrab(time_: builtins.int) -> None: ...


def keyval_convert_case(symbol: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def keyval_from_name(keyval_name: builtins.str) -> builtins.int: ...


def keyval_is_lower(keyval: builtins.int) -> builtins.bool: ...


def keyval_is_upper(keyval: builtins.int) -> builtins.bool: ...


def keyval_name(keyval: builtins.int) -> typing.Optional[builtins.str]: ...


def keyval_to_lower(keyval: builtins.int) -> builtins.int: ...


def keyval_to_unicode(keyval: builtins.int) -> builtins.int: ...


def keyval_to_upper(keyval: builtins.int) -> builtins.int: ...


def list_visuals() -> typing.Sequence[Visual]: ...


def notify_startup_complete() -> None: ...


def notify_startup_complete_with_id(startup_id: builtins.str) -> None: ...


def offscreen_window_get_embedder(window: Window) -> typing.Optional[Window]: ...


def offscreen_window_get_surface(window: Window) -> typing.Optional[cairo.Surface]: ...


def offscreen_window_set_embedder(window: Window, embedder: Window) -> None: ...


def pango_context_get() -> Pango.Context: ...


def pango_context_get_for_display(display: Display) -> Pango.Context: ...


def pango_context_get_for_screen(screen: Screen) -> Pango.Context: ...


def parse_args(argv: typing.Sequence[builtins.str]) -> typing.Sequence[builtins.str]: ...


def pixbuf_get_from_surface(surface: cairo.Surface, src_x: builtins.int, src_y: builtins.int, width: builtins.int, height: builtins.int) -> typing.Optional[GdkPixbuf.Pixbuf]: ...


def pixbuf_get_from_window(window: Window, src_x: builtins.int, src_y: builtins.int, width: builtins.int, height: builtins.int) -> typing.Optional[GdkPixbuf.Pixbuf]: ...


def pointer_grab(window: Window, owner_events: builtins.bool, event_mask: EventMask, confine_to: typing.Optional[Window], cursor: typing.Optional[Cursor], time_: builtins.int) -> GrabStatus: ...


def pointer_is_grabbed() -> builtins.bool: ...


def pointer_ungrab(time_: builtins.int) -> None: ...


def pre_parse_libgtk_only() -> None: ...


def property_delete(window: Window, property: Atom) -> None: ...


def property_get(window: Window, property: Atom, type: Atom, offset: builtins.int, length: builtins.int, pdelete: builtins.int) -> typing.Tuple[builtins.bool, Atom, builtins.int, builtins.bytes]: ...


def query_depths() -> typing.Sequence[builtins.int]: ...


def query_visual_types() -> typing.Sequence[VisualType]: ...


def selection_convert(requestor: Window, selection: Atom, target: Atom, time_: builtins.int) -> None: ...


def selection_owner_get(selection: Atom) -> typing.Optional[Window]: ...


def selection_owner_get_for_display(display: Display, selection: Atom) -> typing.Optional[Window]: ...


def selection_owner_set(owner: typing.Optional[Window], selection: Atom, time_: builtins.int, send_event: builtins.bool) -> builtins.bool: ...


def selection_owner_set_for_display(display: Display, owner: typing.Optional[Window], selection: Atom, time_: builtins.int, send_event: builtins.bool) -> builtins.bool: ...


def selection_send_notify(requestor: Window, selection: Atom, target: Atom, property: Atom, time_: builtins.int) -> None: ...


def selection_send_notify_for_display(display: Display, requestor: Window, selection: Atom, target: Atom, property: Atom, time_: builtins.int) -> None: ...


def set_allowed_backends(backends: builtins.str) -> None: ...


def set_double_click_time(msec: builtins.int) -> None: ...


def set_program_class(program_class: builtins.str) -> None: ...


def set_show_events(show_events: builtins.bool) -> None: ...


def setting_get(name: builtins.str, value: GObject.Value) -> builtins.bool: ...


def synthesize_window_state(window: Window, unset_flags: WindowState, set_flags: WindowState) -> None: ...


def test_render_sync(window: Window) -> None: ...


def test_simulate_button(window: Window, x: builtins.int, y: builtins.int, button: builtins.int, modifiers: ModifierType, button_pressrelease: EventType) -> builtins.bool: ...


def test_simulate_key(window: Window, x: builtins.int, y: builtins.int, keyval: builtins.int, modifiers: ModifierType, key_pressrelease: EventType) -> builtins.bool: ...


def text_property_to_utf8_list_for_display(display: Display, encoding: Atom, format: builtins.int, text: builtins.bytes) -> typing.Tuple[builtins.int, typing.Sequence[builtins.str]]: ...


def threads_add_idle(priority: builtins.int, function: GLib.SourceFunc, *data: typing.Optional[builtins.object]) -> builtins.int: ...


def threads_add_timeout(priority: builtins.int, interval: builtins.int, function: GLib.SourceFunc, *data: typing.Optional[builtins.object]) -> builtins.int: ...


def threads_add_timeout_seconds(priority: builtins.int, interval: builtins.int, function: GLib.SourceFunc, *data: typing.Optional[builtins.object]) -> builtins.int: ...


def threads_enter() -> None: ...


def threads_init() -> None: ...


def threads_leave() -> None: ...


def unicode_to_keyval(wc: builtins.int) -> builtins.int: ...


def utf8_to_string_target(str: builtins.str) -> typing.Optional[builtins.str]: ...


BUTTON_MIDDLE: builtins.int
BUTTON_PRIMARY: builtins.int
BUTTON_SECONDARY: builtins.int
CURRENT_TIME: builtins.int
EVENT_PROPAGATE: builtins.int
EVENT_STOP: builtins.int
KEY_0: builtins.int
KEY_1: builtins.int
KEY_2: builtins.int
KEY_3: builtins.int
KEY_3270_AltCursor: builtins.int
KEY_3270_Attn: builtins.int
KEY_3270_BackTab: builtins.int
KEY_3270_ChangeScreen: builtins.int
KEY_3270_Copy: builtins.int
KEY_3270_CursorBlink: builtins.int
KEY_3270_CursorSelect: builtins.int
KEY_3270_DeleteWord: builtins.int
KEY_3270_Duplicate: builtins.int
KEY_3270_Enter: builtins.int
KEY_3270_EraseEOF: builtins.int
KEY_3270_EraseInput: builtins.int
KEY_3270_ExSelect: builtins.int
KEY_3270_FieldMark: builtins.int
KEY_3270_Ident: builtins.int
KEY_3270_Jump: builtins.int
KEY_3270_KeyClick: builtins.int
KEY_3270_Left2: builtins.int
KEY_3270_PA1: builtins.int
KEY_3270_PA2: builtins.int
KEY_3270_PA3: builtins.int
KEY_3270_Play: builtins.int
KEY_3270_PrintScreen: builtins.int
KEY_3270_Quit: builtins.int
KEY_3270_Record: builtins.int
KEY_3270_Reset: builtins.int
KEY_3270_Right2: builtins.int
KEY_3270_Rule: builtins.int
KEY_3270_Setup: builtins.int
KEY_3270_Test: builtins.int
KEY_4: builtins.int
KEY_5: builtins.int
KEY_6: builtins.int
KEY_7: builtins.int
KEY_8: builtins.int
KEY_9: builtins.int
KEY_A: builtins.int
KEY_AE: builtins.int
KEY_Aacute: builtins.int
KEY_Abelowdot: builtins.int
KEY_Abreve: builtins.int
KEY_Abreveacute: builtins.int
KEY_Abrevebelowdot: builtins.int
KEY_Abrevegrave: builtins.int
KEY_Abrevehook: builtins.int
KEY_Abrevetilde: builtins.int
KEY_AccessX_Enable: builtins.int
KEY_AccessX_Feedback_Enable: builtins.int
KEY_Acircumflex: builtins.int
KEY_Acircumflexacute: builtins.int
KEY_Acircumflexbelowdot: builtins.int
KEY_Acircumflexgrave: builtins.int
KEY_Acircumflexhook: builtins.int
KEY_Acircumflextilde: builtins.int
KEY_AddFavorite: builtins.int
KEY_Adiaeresis: builtins.int
KEY_Agrave: builtins.int
KEY_Ahook: builtins.int
KEY_Alt_L: builtins.int
KEY_Alt_R: builtins.int
KEY_Amacron: builtins.int
KEY_Aogonek: builtins.int
KEY_ApplicationLeft: builtins.int
KEY_ApplicationRight: builtins.int
KEY_Arabic_0: builtins.int
KEY_Arabic_1: builtins.int
KEY_Arabic_2: builtins.int
KEY_Arabic_3: builtins.int
KEY_Arabic_4: builtins.int
KEY_Arabic_5: builtins.int
KEY_Arabic_6: builtins.int
KEY_Arabic_7: builtins.int
KEY_Arabic_8: builtins.int
KEY_Arabic_9: builtins.int
KEY_Arabic_ain: builtins.int
KEY_Arabic_alef: builtins.int
KEY_Arabic_alefmaksura: builtins.int
KEY_Arabic_beh: builtins.int
KEY_Arabic_comma: builtins.int
KEY_Arabic_dad: builtins.int
KEY_Arabic_dal: builtins.int
KEY_Arabic_damma: builtins.int
KEY_Arabic_dammatan: builtins.int
KEY_Arabic_ddal: builtins.int
KEY_Arabic_farsi_yeh: builtins.int
KEY_Arabic_fatha: builtins.int
KEY_Arabic_fathatan: builtins.int
KEY_Arabic_feh: builtins.int
KEY_Arabic_fullstop: builtins.int
KEY_Arabic_gaf: builtins.int
KEY_Arabic_ghain: builtins.int
KEY_Arabic_ha: builtins.int
KEY_Arabic_hah: builtins.int
KEY_Arabic_hamza: builtins.int
KEY_Arabic_hamza_above: builtins.int
KEY_Arabic_hamza_below: builtins.int
KEY_Arabic_hamzaonalef: builtins.int
KEY_Arabic_hamzaonwaw: builtins.int
KEY_Arabic_hamzaonyeh: builtins.int
KEY_Arabic_hamzaunderalef: builtins.int
KEY_Arabic_heh: builtins.int
KEY_Arabic_heh_doachashmee: builtins.int
KEY_Arabic_heh_goal: builtins.int
KEY_Arabic_jeem: builtins.int
KEY_Arabic_jeh: builtins.int
KEY_Arabic_kaf: builtins.int
KEY_Arabic_kasra: builtins.int
KEY_Arabic_kasratan: builtins.int
KEY_Arabic_keheh: builtins.int
KEY_Arabic_khah: builtins.int
KEY_Arabic_lam: builtins.int
KEY_Arabic_madda_above: builtins.int
KEY_Arabic_maddaonalef: builtins.int
KEY_Arabic_meem: builtins.int
KEY_Arabic_noon: builtins.int
KEY_Arabic_noon_ghunna: builtins.int
KEY_Arabic_peh: builtins.int
KEY_Arabic_percent: builtins.int
KEY_Arabic_qaf: builtins.int
KEY_Arabic_question_mark: builtins.int
KEY_Arabic_ra: builtins.int
KEY_Arabic_rreh: builtins.int
KEY_Arabic_sad: builtins.int
KEY_Arabic_seen: builtins.int
KEY_Arabic_semicolon: builtins.int
KEY_Arabic_shadda: builtins.int
KEY_Arabic_sheen: builtins.int
KEY_Arabic_sukun: builtins.int
KEY_Arabic_superscript_alef: builtins.int
KEY_Arabic_switch: builtins.int
KEY_Arabic_tah: builtins.int
KEY_Arabic_tatweel: builtins.int
KEY_Arabic_tcheh: builtins.int
KEY_Arabic_teh: builtins.int
KEY_Arabic_tehmarbuta: builtins.int
KEY_Arabic_thal: builtins.int
KEY_Arabic_theh: builtins.int
KEY_Arabic_tteh: builtins.int
KEY_Arabic_veh: builtins.int
KEY_Arabic_waw: builtins.int
KEY_Arabic_yeh: builtins.int
KEY_Arabic_yeh_baree: builtins.int
KEY_Arabic_zah: builtins.int
KEY_Arabic_zain: builtins.int
KEY_Aring: builtins.int
KEY_Armenian_AT: builtins.int
KEY_Armenian_AYB: builtins.int
KEY_Armenian_BEN: builtins.int
KEY_Armenian_CHA: builtins.int
KEY_Armenian_DA: builtins.int
KEY_Armenian_DZA: builtins.int
KEY_Armenian_E: builtins.int
KEY_Armenian_FE: builtins.int
KEY_Armenian_GHAT: builtins.int
KEY_Armenian_GIM: builtins.int
KEY_Armenian_HI: builtins.int
KEY_Armenian_HO: builtins.int
KEY_Armenian_INI: builtins.int
KEY_Armenian_JE: builtins.int
KEY_Armenian_KE: builtins.int
KEY_Armenian_KEN: builtins.int
KEY_Armenian_KHE: builtins.int
KEY_Armenian_LYUN: builtins.int
KEY_Armenian_MEN: builtins.int
KEY_Armenian_NU: builtins.int
KEY_Armenian_O: builtins.int
KEY_Armenian_PE: builtins.int
KEY_Armenian_PYUR: builtins.int
KEY_Armenian_RA: builtins.int
KEY_Armenian_RE: builtins.int
KEY_Armenian_SE: builtins.int
KEY_Armenian_SHA: builtins.int
KEY_Armenian_TCHE: builtins.int
KEY_Armenian_TO: builtins.int
KEY_Armenian_TSA: builtins.int
KEY_Armenian_TSO: builtins.int
KEY_Armenian_TYUN: builtins.int
KEY_Armenian_VEV: builtins.int
KEY_Armenian_VO: builtins.int
KEY_Armenian_VYUN: builtins.int
KEY_Armenian_YECH: builtins.int
KEY_Armenian_ZA: builtins.int
KEY_Armenian_ZHE: builtins.int
KEY_Armenian_accent: builtins.int
KEY_Armenian_amanak: builtins.int
KEY_Armenian_apostrophe: builtins.int
KEY_Armenian_at: builtins.int
KEY_Armenian_ayb: builtins.int
KEY_Armenian_ben: builtins.int
KEY_Armenian_but: builtins.int
KEY_Armenian_cha: builtins.int
KEY_Armenian_da: builtins.int
KEY_Armenian_dza: builtins.int
KEY_Armenian_e: builtins.int
KEY_Armenian_exclam: builtins.int
KEY_Armenian_fe: builtins.int
KEY_Armenian_full_stop: builtins.int
KEY_Armenian_ghat: builtins.int
KEY_Armenian_gim: builtins.int
KEY_Armenian_hi: builtins.int
KEY_Armenian_ho: builtins.int
KEY_Armenian_hyphen: builtins.int
KEY_Armenian_ini: builtins.int
KEY_Armenian_je: builtins.int
KEY_Armenian_ke: builtins.int
KEY_Armenian_ken: builtins.int
KEY_Armenian_khe: builtins.int
KEY_Armenian_ligature_ew: builtins.int
KEY_Armenian_lyun: builtins.int
KEY_Armenian_men: builtins.int
KEY_Armenian_nu: builtins.int
KEY_Armenian_o: builtins.int
KEY_Armenian_paruyk: builtins.int
KEY_Armenian_pe: builtins.int
KEY_Armenian_pyur: builtins.int
KEY_Armenian_question: builtins.int
KEY_Armenian_ra: builtins.int
KEY_Armenian_re: builtins.int
KEY_Armenian_se: builtins.int
KEY_Armenian_separation_mark: builtins.int
KEY_Armenian_sha: builtins.int
KEY_Armenian_shesht: builtins.int
KEY_Armenian_tche: builtins.int
KEY_Armenian_to: builtins.int
KEY_Armenian_tsa: builtins.int
KEY_Armenian_tso: builtins.int
KEY_Armenian_tyun: builtins.int
KEY_Armenian_verjaket: builtins.int
KEY_Armenian_vev: builtins.int
KEY_Armenian_vo: builtins.int
KEY_Armenian_vyun: builtins.int
KEY_Armenian_yech: builtins.int
KEY_Armenian_yentamna: builtins.int
KEY_Armenian_za: builtins.int
KEY_Armenian_zhe: builtins.int
KEY_Atilde: builtins.int
KEY_AudibleBell_Enable: builtins.int
KEY_AudioCycleTrack: builtins.int
KEY_AudioForward: builtins.int
KEY_AudioLowerVolume: builtins.int
KEY_AudioMedia: builtins.int
KEY_AudioMicMute: builtins.int
KEY_AudioMute: builtins.int
KEY_AudioNext: builtins.int
KEY_AudioPause: builtins.int
KEY_AudioPlay: builtins.int
KEY_AudioPreset: builtins.int
KEY_AudioPrev: builtins.int
KEY_AudioRaiseVolume: builtins.int
KEY_AudioRandomPlay: builtins.int
KEY_AudioRecord: builtins.int
KEY_AudioRepeat: builtins.int
KEY_AudioRewind: builtins.int
KEY_AudioStop: builtins.int
KEY_Away: builtins.int
KEY_B: builtins.int
KEY_Babovedot: builtins.int
KEY_Back: builtins.int
KEY_BackForward: builtins.int
KEY_BackSpace: builtins.int
KEY_Battery: builtins.int
KEY_Begin: builtins.int
KEY_Blue: builtins.int
KEY_Bluetooth: builtins.int
KEY_Book: builtins.int
KEY_BounceKeys_Enable: builtins.int
KEY_Break: builtins.int
KEY_BrightnessAdjust: builtins.int
KEY_Byelorussian_SHORTU: builtins.int
KEY_Byelorussian_shortu: builtins.int
KEY_C: builtins.int
KEY_CD: builtins.int
KEY_CH: builtins.int
KEY_C_H: builtins.int
KEY_C_h: builtins.int
KEY_Cabovedot: builtins.int
KEY_Cacute: builtins.int
KEY_Calculator: builtins.int
KEY_Calendar: builtins.int
KEY_Cancel: builtins.int
KEY_Caps_Lock: builtins.int
KEY_Ccaron: builtins.int
KEY_Ccedilla: builtins.int
KEY_Ccircumflex: builtins.int
KEY_Ch: builtins.int
KEY_Clear: builtins.int
KEY_ClearGrab: builtins.int
KEY_Close: builtins.int
KEY_Codeinput: builtins.int
KEY_ColonSign: builtins.int
KEY_Community: builtins.int
KEY_ContrastAdjust: builtins.int
KEY_Control_L: builtins.int
KEY_Control_R: builtins.int
KEY_Copy: builtins.int
KEY_CruzeiroSign: builtins.int
KEY_Cut: builtins.int
KEY_CycleAngle: builtins.int
KEY_Cyrillic_A: builtins.int
KEY_Cyrillic_BE: builtins.int
KEY_Cyrillic_CHE: builtins.int
KEY_Cyrillic_CHE_descender: builtins.int
KEY_Cyrillic_CHE_vertstroke: builtins.int
KEY_Cyrillic_DE: builtins.int
KEY_Cyrillic_DZHE: builtins.int
KEY_Cyrillic_E: builtins.int
KEY_Cyrillic_EF: builtins.int
KEY_Cyrillic_EL: builtins.int
KEY_Cyrillic_EM: builtins.int
KEY_Cyrillic_EN: builtins.int
KEY_Cyrillic_EN_descender: builtins.int
KEY_Cyrillic_ER: builtins.int
KEY_Cyrillic_ES: builtins.int
KEY_Cyrillic_GHE: builtins.int
KEY_Cyrillic_GHE_bar: builtins.int
KEY_Cyrillic_HA: builtins.int
KEY_Cyrillic_HARDSIGN: builtins.int
KEY_Cyrillic_HA_descender: builtins.int
KEY_Cyrillic_I: builtins.int
KEY_Cyrillic_IE: builtins.int
KEY_Cyrillic_IO: builtins.int
KEY_Cyrillic_I_macron: builtins.int
KEY_Cyrillic_JE: builtins.int
KEY_Cyrillic_KA: builtins.int
KEY_Cyrillic_KA_descender: builtins.int
KEY_Cyrillic_KA_vertstroke: builtins.int
KEY_Cyrillic_LJE: builtins.int
KEY_Cyrillic_NJE: builtins.int
KEY_Cyrillic_O: builtins.int
KEY_Cyrillic_O_bar: builtins.int
KEY_Cyrillic_PE: builtins.int
KEY_Cyrillic_SCHWA: builtins.int
KEY_Cyrillic_SHA: builtins.int
KEY_Cyrillic_SHCHA: builtins.int
KEY_Cyrillic_SHHA: builtins.int
KEY_Cyrillic_SHORTI: builtins.int
KEY_Cyrillic_SOFTSIGN: builtins.int
KEY_Cyrillic_TE: builtins.int
KEY_Cyrillic_TSE: builtins.int
KEY_Cyrillic_U: builtins.int
KEY_Cyrillic_U_macron: builtins.int
KEY_Cyrillic_U_straight: builtins.int
KEY_Cyrillic_U_straight_bar: builtins.int
KEY_Cyrillic_VE: builtins.int
KEY_Cyrillic_YA: builtins.int
KEY_Cyrillic_YERU: builtins.int
KEY_Cyrillic_YU: builtins.int
KEY_Cyrillic_ZE: builtins.int
KEY_Cyrillic_ZHE: builtins.int
KEY_Cyrillic_ZHE_descender: builtins.int
KEY_Cyrillic_a: builtins.int
KEY_Cyrillic_be: builtins.int
KEY_Cyrillic_che: builtins.int
KEY_Cyrillic_che_descender: builtins.int
KEY_Cyrillic_che_vertstroke: builtins.int
KEY_Cyrillic_de: builtins.int
KEY_Cyrillic_dzhe: builtins.int
KEY_Cyrillic_e: builtins.int
KEY_Cyrillic_ef: builtins.int
KEY_Cyrillic_el: builtins.int
KEY_Cyrillic_em: builtins.int
KEY_Cyrillic_en: builtins.int
KEY_Cyrillic_en_descender: builtins.int
KEY_Cyrillic_er: builtins.int
KEY_Cyrillic_es: builtins.int
KEY_Cyrillic_ghe: builtins.int
KEY_Cyrillic_ghe_bar: builtins.int
KEY_Cyrillic_ha: builtins.int
KEY_Cyrillic_ha_descender: builtins.int
KEY_Cyrillic_hardsign: builtins.int
KEY_Cyrillic_i: builtins.int
KEY_Cyrillic_i_macron: builtins.int
KEY_Cyrillic_ie: builtins.int
KEY_Cyrillic_io: builtins.int
KEY_Cyrillic_je: builtins.int
KEY_Cyrillic_ka: builtins.int
KEY_Cyrillic_ka_descender: builtins.int
KEY_Cyrillic_ka_vertstroke: builtins.int
KEY_Cyrillic_lje: builtins.int
KEY_Cyrillic_nje: builtins.int
KEY_Cyrillic_o: builtins.int
KEY_Cyrillic_o_bar: builtins.int
KEY_Cyrillic_pe: builtins.int
KEY_Cyrillic_schwa: builtins.int
KEY_Cyrillic_sha: builtins.int
KEY_Cyrillic_shcha: builtins.int
KEY_Cyrillic_shha: builtins.int
KEY_Cyrillic_shorti: builtins.int
KEY_Cyrillic_softsign: builtins.int
KEY_Cyrillic_te: builtins.int
KEY_Cyrillic_tse: builtins.int
KEY_Cyrillic_u: builtins.int
KEY_Cyrillic_u_macron: builtins.int
KEY_Cyrillic_u_straight: builtins.int
KEY_Cyrillic_u_straight_bar: builtins.int
KEY_Cyrillic_ve: builtins.int
KEY_Cyrillic_ya: builtins.int
KEY_Cyrillic_yeru: builtins.int
KEY_Cyrillic_yu: builtins.int
KEY_Cyrillic_ze: builtins.int
KEY_Cyrillic_zhe: builtins.int
KEY_Cyrillic_zhe_descender: builtins.int
KEY_D: builtins.int
KEY_DOS: builtins.int
KEY_Dabovedot: builtins.int
KEY_Dcaron: builtins.int
KEY_Delete: builtins.int
KEY_Display: builtins.int
KEY_Documents: builtins.int
KEY_DongSign: builtins.int
KEY_Down: builtins.int
KEY_Dstroke: builtins.int
KEY_E: builtins.int
KEY_ENG: builtins.int
KEY_ETH: builtins.int
KEY_EZH: builtins.int
KEY_Eabovedot: builtins.int
KEY_Eacute: builtins.int
KEY_Ebelowdot: builtins.int
KEY_Ecaron: builtins.int
KEY_Ecircumflex: builtins.int
KEY_Ecircumflexacute: builtins.int
KEY_Ecircumflexbelowdot: builtins.int
KEY_Ecircumflexgrave: builtins.int
KEY_Ecircumflexhook: builtins.int
KEY_Ecircumflextilde: builtins.int
KEY_EcuSign: builtins.int
KEY_Ediaeresis: builtins.int
KEY_Egrave: builtins.int
KEY_Ehook: builtins.int
KEY_Eisu_Shift: builtins.int
KEY_Eisu_toggle: builtins.int
KEY_Eject: builtins.int
KEY_Emacron: builtins.int
KEY_End: builtins.int
KEY_Eogonek: builtins.int
KEY_Escape: builtins.int
KEY_Eth: builtins.int
KEY_Etilde: builtins.int
KEY_EuroSign: builtins.int
KEY_Excel: builtins.int
KEY_Execute: builtins.int
KEY_Explorer: builtins.int
KEY_F: builtins.int
KEY_F1: builtins.int
KEY_F10: builtins.int
KEY_F11: builtins.int
KEY_F12: builtins.int
KEY_F13: builtins.int
KEY_F14: builtins.int
KEY_F15: builtins.int
KEY_F16: builtins.int
KEY_F17: builtins.int
KEY_F18: builtins.int
KEY_F19: builtins.int
KEY_F2: builtins.int
KEY_F20: builtins.int
KEY_F21: builtins.int
KEY_F22: builtins.int
KEY_F23: builtins.int
KEY_F24: builtins.int
KEY_F25: builtins.int
KEY_F26: builtins.int
KEY_F27: builtins.int
KEY_F28: builtins.int
KEY_F29: builtins.int
KEY_F3: builtins.int
KEY_F30: builtins.int
KEY_F31: builtins.int
KEY_F32: builtins.int
KEY_F33: builtins.int
KEY_F34: builtins.int
KEY_F35: builtins.int
KEY_F4: builtins.int
KEY_F5: builtins.int
KEY_F6: builtins.int
KEY_F7: builtins.int
KEY_F8: builtins.int
KEY_F9: builtins.int
KEY_FFrancSign: builtins.int
KEY_Fabovedot: builtins.int
KEY_Farsi_0: builtins.int
KEY_Farsi_1: builtins.int
KEY_Farsi_2: builtins.int
KEY_Farsi_3: builtins.int
KEY_Farsi_4: builtins.int
KEY_Farsi_5: builtins.int
KEY_Farsi_6: builtins.int
KEY_Farsi_7: builtins.int
KEY_Farsi_8: builtins.int
KEY_Farsi_9: builtins.int
KEY_Farsi_yeh: builtins.int
KEY_Favorites: builtins.int
KEY_Finance: builtins.int
KEY_Find: builtins.int
KEY_First_Virtual_Screen: builtins.int
KEY_Forward: builtins.int
KEY_FrameBack: builtins.int
KEY_FrameForward: builtins.int
KEY_G: builtins.int
KEY_Gabovedot: builtins.int
KEY_Game: builtins.int
KEY_Gbreve: builtins.int
KEY_Gcaron: builtins.int
KEY_Gcedilla: builtins.int
KEY_Gcircumflex: builtins.int
KEY_Georgian_an: builtins.int
KEY_Georgian_ban: builtins.int
KEY_Georgian_can: builtins.int
KEY_Georgian_char: builtins.int
KEY_Georgian_chin: builtins.int
KEY_Georgian_cil: builtins.int
KEY_Georgian_don: builtins.int
KEY_Georgian_en: builtins.int
KEY_Georgian_fi: builtins.int
KEY_Georgian_gan: builtins.int
KEY_Georgian_ghan: builtins.int
KEY_Georgian_hae: builtins.int
KEY_Georgian_har: builtins.int
KEY_Georgian_he: builtins.int
KEY_Georgian_hie: builtins.int
KEY_Georgian_hoe: builtins.int
KEY_Georgian_in: builtins.int
KEY_Georgian_jhan: builtins.int
KEY_Georgian_jil: builtins.int
KEY_Georgian_kan: builtins.int
KEY_Georgian_khar: builtins.int
KEY_Georgian_las: builtins.int
KEY_Georgian_man: builtins.int
KEY_Georgian_nar: builtins.int
KEY_Georgian_on: builtins.int
KEY_Georgian_par: builtins.int
KEY_Georgian_phar: builtins.int
KEY_Georgian_qar: builtins.int
KEY_Georgian_rae: builtins.int
KEY_Georgian_san: builtins.int
KEY_Georgian_shin: builtins.int
KEY_Georgian_tan: builtins.int
KEY_Georgian_tar: builtins.int
KEY_Georgian_un: builtins.int
KEY_Georgian_vin: builtins.int
KEY_Georgian_we: builtins.int
KEY_Georgian_xan: builtins.int
KEY_Georgian_zen: builtins.int
KEY_Georgian_zhar: builtins.int
KEY_Go: builtins.int
KEY_Greek_ALPHA: builtins.int
KEY_Greek_ALPHAaccent: builtins.int
KEY_Greek_BETA: builtins.int
KEY_Greek_CHI: builtins.int
KEY_Greek_DELTA: builtins.int
KEY_Greek_EPSILON: builtins.int
KEY_Greek_EPSILONaccent: builtins.int
KEY_Greek_ETA: builtins.int
KEY_Greek_ETAaccent: builtins.int
KEY_Greek_GAMMA: builtins.int
KEY_Greek_IOTA: builtins.int
KEY_Greek_IOTAaccent: builtins.int
KEY_Greek_IOTAdiaeresis: builtins.int
KEY_Greek_IOTAdieresis: builtins.int
KEY_Greek_KAPPA: builtins.int
KEY_Greek_LAMBDA: builtins.int
KEY_Greek_LAMDA: builtins.int
KEY_Greek_MU: builtins.int
KEY_Greek_NU: builtins.int
KEY_Greek_OMEGA: builtins.int
KEY_Greek_OMEGAaccent: builtins.int
KEY_Greek_OMICRON: builtins.int
KEY_Greek_OMICRONaccent: builtins.int
KEY_Greek_PHI: builtins.int
KEY_Greek_PI: builtins.int
KEY_Greek_PSI: builtins.int
KEY_Greek_RHO: builtins.int
KEY_Greek_SIGMA: builtins.int
KEY_Greek_TAU: builtins.int
KEY_Greek_THETA: builtins.int
KEY_Greek_UPSILON: builtins.int
KEY_Greek_UPSILONaccent: builtins.int
KEY_Greek_UPSILONdieresis: builtins.int
KEY_Greek_XI: builtins.int
KEY_Greek_ZETA: builtins.int
KEY_Greek_accentdieresis: builtins.int
KEY_Greek_alpha: builtins.int
KEY_Greek_alphaaccent: builtins.int
KEY_Greek_beta: builtins.int
KEY_Greek_chi: builtins.int
KEY_Greek_delta: builtins.int
KEY_Greek_epsilon: builtins.int
KEY_Greek_epsilonaccent: builtins.int
KEY_Greek_eta: builtins.int
KEY_Greek_etaaccent: builtins.int
KEY_Greek_finalsmallsigma: builtins.int
KEY_Greek_gamma: builtins.int
KEY_Greek_horizbar: builtins.int
KEY_Greek_iota: builtins.int
KEY_Greek_iotaaccent: builtins.int
KEY_Greek_iotaaccentdieresis: builtins.int
KEY_Greek_iotadieresis: builtins.int
KEY_Greek_kappa: builtins.int
KEY_Greek_lambda: builtins.int
KEY_Greek_lamda: builtins.int
KEY_Greek_mu: builtins.int
KEY_Greek_nu: builtins.int
KEY_Greek_omega: builtins.int
KEY_Greek_omegaaccent: builtins.int
KEY_Greek_omicron: builtins.int
KEY_Greek_omicronaccent: builtins.int
KEY_Greek_phi: builtins.int
KEY_Greek_pi: builtins.int
KEY_Greek_psi: builtins.int
KEY_Greek_rho: builtins.int
KEY_Greek_sigma: builtins.int
KEY_Greek_switch: builtins.int
KEY_Greek_tau: builtins.int
KEY_Greek_theta: builtins.int
KEY_Greek_upsilon: builtins.int
KEY_Greek_upsilonaccent: builtins.int
KEY_Greek_upsilonaccentdieresis: builtins.int
KEY_Greek_upsilondieresis: builtins.int
KEY_Greek_xi: builtins.int
KEY_Greek_zeta: builtins.int
KEY_Green: builtins.int
KEY_H: builtins.int
KEY_Hangul: builtins.int
KEY_Hangul_A: builtins.int
KEY_Hangul_AE: builtins.int
KEY_Hangul_AraeA: builtins.int
KEY_Hangul_AraeAE: builtins.int
KEY_Hangul_Banja: builtins.int
KEY_Hangul_Cieuc: builtins.int
KEY_Hangul_Codeinput: builtins.int
KEY_Hangul_Dikeud: builtins.int
KEY_Hangul_E: builtins.int
KEY_Hangul_EO: builtins.int
KEY_Hangul_EU: builtins.int
KEY_Hangul_End: builtins.int
KEY_Hangul_Hanja: builtins.int
KEY_Hangul_Hieuh: builtins.int
KEY_Hangul_I: builtins.int
KEY_Hangul_Ieung: builtins.int
KEY_Hangul_J_Cieuc: builtins.int
KEY_Hangul_J_Dikeud: builtins.int
KEY_Hangul_J_Hieuh: builtins.int
KEY_Hangul_J_Ieung: builtins.int
KEY_Hangul_J_Jieuj: builtins.int
KEY_Hangul_J_Khieuq: builtins.int
KEY_Hangul_J_Kiyeog: builtins.int
KEY_Hangul_J_KiyeogSios: builtins.int
KEY_Hangul_J_KkogjiDalrinIeung: builtins.int
KEY_Hangul_J_Mieum: builtins.int
KEY_Hangul_J_Nieun: builtins.int
KEY_Hangul_J_NieunHieuh: builtins.int
KEY_Hangul_J_NieunJieuj: builtins.int
KEY_Hangul_J_PanSios: builtins.int
KEY_Hangul_J_Phieuf: builtins.int
KEY_Hangul_J_Pieub: builtins.int
KEY_Hangul_J_PieubSios: builtins.int
KEY_Hangul_J_Rieul: builtins.int
KEY_Hangul_J_RieulHieuh: builtins.int
KEY_Hangul_J_RieulKiyeog: builtins.int
KEY_Hangul_J_RieulMieum: builtins.int
KEY_Hangul_J_RieulPhieuf: builtins.int
KEY_Hangul_J_RieulPieub: builtins.int
KEY_Hangul_J_RieulSios: builtins.int
KEY_Hangul_J_RieulTieut: builtins.int
KEY_Hangul_J_Sios: builtins.int
KEY_Hangul_J_SsangKiyeog: builtins.int
KEY_Hangul_J_SsangSios: builtins.int
KEY_Hangul_J_Tieut: builtins.int
KEY_Hangul_J_YeorinHieuh: builtins.int
KEY_Hangul_Jamo: builtins.int
KEY_Hangul_Jeonja: builtins.int
KEY_Hangul_Jieuj: builtins.int
KEY_Hangul_Khieuq: builtins.int
KEY_Hangul_Kiyeog: builtins.int
KEY_Hangul_KiyeogSios: builtins.int
KEY_Hangul_KkogjiDalrinIeung: builtins.int
KEY_Hangul_Mieum: builtins.int
KEY_Hangul_MultipleCandidate: builtins.int
KEY_Hangul_Nieun: builtins.int
KEY_Hangul_NieunHieuh: builtins.int
KEY_Hangul_NieunJieuj: builtins.int
KEY_Hangul_O: builtins.int
KEY_Hangul_OE: builtins.int
KEY_Hangul_PanSios: builtins.int
KEY_Hangul_Phieuf: builtins.int
KEY_Hangul_Pieub: builtins.int
KEY_Hangul_PieubSios: builtins.int
KEY_Hangul_PostHanja: builtins.int
KEY_Hangul_PreHanja: builtins.int
KEY_Hangul_PreviousCandidate: builtins.int
KEY_Hangul_Rieul: builtins.int
KEY_Hangul_RieulHieuh: builtins.int
KEY_Hangul_RieulKiyeog: builtins.int
KEY_Hangul_RieulMieum: builtins.int
KEY_Hangul_RieulPhieuf: builtins.int
KEY_Hangul_RieulPieub: builtins.int
KEY_Hangul_RieulSios: builtins.int
KEY_Hangul_RieulTieut: builtins.int
KEY_Hangul_RieulYeorinHieuh: builtins.int
KEY_Hangul_Romaja: builtins.int
KEY_Hangul_SingleCandidate: builtins.int
KEY_Hangul_Sios: builtins.int
KEY_Hangul_Special: builtins.int
KEY_Hangul_SsangDikeud: builtins.int
KEY_Hangul_SsangJieuj: builtins.int
KEY_Hangul_SsangKiyeog: builtins.int
KEY_Hangul_SsangPieub: builtins.int
KEY_Hangul_SsangSios: builtins.int
KEY_Hangul_Start: builtins.int
KEY_Hangul_SunkyeongeumMieum: builtins.int
KEY_Hangul_SunkyeongeumPhieuf: builtins.int
KEY_Hangul_SunkyeongeumPieub: builtins.int
KEY_Hangul_Tieut: builtins.int
KEY_Hangul_U: builtins.int
KEY_Hangul_WA: builtins.int
KEY_Hangul_WAE: builtins.int
KEY_Hangul_WE: builtins.int
KEY_Hangul_WEO: builtins.int
KEY_Hangul_WI: builtins.int
KEY_Hangul_YA: builtins.int
KEY_Hangul_YAE: builtins.int
KEY_Hangul_YE: builtins.int
KEY_Hangul_YEO: builtins.int
KEY_Hangul_YI: builtins.int
KEY_Hangul_YO: builtins.int
KEY_Hangul_YU: builtins.int
KEY_Hangul_YeorinHieuh: builtins.int
KEY_Hangul_switch: builtins.int
KEY_Hankaku: builtins.int
KEY_Hcircumflex: builtins.int
KEY_Hebrew_switch: builtins.int
KEY_Help: builtins.int
KEY_Henkan: builtins.int
KEY_Henkan_Mode: builtins.int
KEY_Hibernate: builtins.int
KEY_Hiragana: builtins.int
KEY_Hiragana_Katakana: builtins.int
KEY_History: builtins.int
KEY_Home: builtins.int
KEY_HomePage: builtins.int
KEY_HotLinks: builtins.int
KEY_Hstroke: builtins.int
KEY_Hyper_L: builtins.int
KEY_Hyper_R: builtins.int
KEY_I: builtins.int
KEY_ISO_Center_Object: builtins.int
KEY_ISO_Continuous_Underline: builtins.int
KEY_ISO_Discontinuous_Underline: builtins.int
KEY_ISO_Emphasize: builtins.int
KEY_ISO_Enter: builtins.int
KEY_ISO_Fast_Cursor_Down: builtins.int
KEY_ISO_Fast_Cursor_Left: builtins.int
KEY_ISO_Fast_Cursor_Right: builtins.int
KEY_ISO_Fast_Cursor_Up: builtins.int
KEY_ISO_First_Group: builtins.int
KEY_ISO_First_Group_Lock: builtins.int
KEY_ISO_Group_Latch: builtins.int
KEY_ISO_Group_Lock: builtins.int
KEY_ISO_Group_Shift: builtins.int
KEY_ISO_Last_Group: builtins.int
KEY_ISO_Last_Group_Lock: builtins.int
KEY_ISO_Left_Tab: builtins.int
KEY_ISO_Level2_Latch: builtins.int
KEY_ISO_Level3_Latch: builtins.int
KEY_ISO_Level3_Lock: builtins.int
KEY_ISO_Level3_Shift: builtins.int
KEY_ISO_Level5_Latch: builtins.int
KEY_ISO_Level5_Lock: builtins.int
KEY_ISO_Level5_Shift: builtins.int
KEY_ISO_Lock: builtins.int
KEY_ISO_Move_Line_Down: builtins.int
KEY_ISO_Move_Line_Up: builtins.int
KEY_ISO_Next_Group: builtins.int
KEY_ISO_Next_Group_Lock: builtins.int
KEY_ISO_Partial_Line_Down: builtins.int
KEY_ISO_Partial_Line_Up: builtins.int
KEY_ISO_Partial_Space_Left: builtins.int
KEY_ISO_Partial_Space_Right: builtins.int
KEY_ISO_Prev_Group: builtins.int
KEY_ISO_Prev_Group_Lock: builtins.int
KEY_ISO_Release_Both_Margins: builtins.int
KEY_ISO_Release_Margin_Left: builtins.int
KEY_ISO_Release_Margin_Right: builtins.int
KEY_ISO_Set_Margin_Left: builtins.int
KEY_ISO_Set_Margin_Right: builtins.int
KEY_Iabovedot: builtins.int
KEY_Iacute: builtins.int
KEY_Ibelowdot: builtins.int
KEY_Ibreve: builtins.int
KEY_Icircumflex: builtins.int
KEY_Idiaeresis: builtins.int
KEY_Igrave: builtins.int
KEY_Ihook: builtins.int
KEY_Imacron: builtins.int
KEY_Insert: builtins.int
KEY_Iogonek: builtins.int
KEY_Itilde: builtins.int
KEY_J: builtins.int
KEY_Jcircumflex: builtins.int
KEY_K: builtins.int
KEY_KP_0: builtins.int
KEY_KP_1: builtins.int
KEY_KP_2: builtins.int
KEY_KP_3: builtins.int
KEY_KP_4: builtins.int
KEY_KP_5: builtins.int
KEY_KP_6: builtins.int
KEY_KP_7: builtins.int
KEY_KP_8: builtins.int
KEY_KP_9: builtins.int
KEY_KP_Add: builtins.int
KEY_KP_Begin: builtins.int
KEY_KP_Decimal: builtins.int
KEY_KP_Delete: builtins.int
KEY_KP_Divide: builtins.int
KEY_KP_Down: builtins.int
KEY_KP_End: builtins.int
KEY_KP_Enter: builtins.int
KEY_KP_Equal: builtins.int
KEY_KP_F1: builtins.int
KEY_KP_F2: builtins.int
KEY_KP_F3: builtins.int
KEY_KP_F4: builtins.int
KEY_KP_Home: builtins.int
KEY_KP_Insert: builtins.int
KEY_KP_Left: builtins.int
KEY_KP_Multiply: builtins.int
KEY_KP_Next: builtins.int
KEY_KP_Page_Down: builtins.int
KEY_KP_Page_Up: builtins.int
KEY_KP_Prior: builtins.int
KEY_KP_Right: builtins.int
KEY_KP_Separator: builtins.int
KEY_KP_Space: builtins.int
KEY_KP_Subtract: builtins.int
KEY_KP_Tab: builtins.int
KEY_KP_Up: builtins.int
KEY_Kana_Lock: builtins.int
KEY_Kana_Shift: builtins.int
KEY_Kanji: builtins.int
KEY_Kanji_Bangou: builtins.int
KEY_Katakana: builtins.int
KEY_KbdBrightnessDown: builtins.int
KEY_KbdBrightnessUp: builtins.int
KEY_KbdLightOnOff: builtins.int
KEY_Kcedilla: builtins.int
KEY_Keyboard: builtins.int
KEY_Korean_Won: builtins.int
KEY_L: builtins.int
KEY_L1: builtins.int
KEY_L10: builtins.int
KEY_L2: builtins.int
KEY_L3: builtins.int
KEY_L4: builtins.int
KEY_L5: builtins.int
KEY_L6: builtins.int
KEY_L7: builtins.int
KEY_L8: builtins.int
KEY_L9: builtins.int
KEY_Lacute: builtins.int
KEY_Last_Virtual_Screen: builtins.int
KEY_Launch0: builtins.int
KEY_Launch1: builtins.int
KEY_Launch2: builtins.int
KEY_Launch3: builtins.int
KEY_Launch4: builtins.int
KEY_Launch5: builtins.int
KEY_Launch6: builtins.int
KEY_Launch7: builtins.int
KEY_Launch8: builtins.int
KEY_Launch9: builtins.int
KEY_LaunchA: builtins.int
KEY_LaunchB: builtins.int
KEY_LaunchC: builtins.int
KEY_LaunchD: builtins.int
KEY_LaunchE: builtins.int
KEY_LaunchF: builtins.int
KEY_Lbelowdot: builtins.int
KEY_Lcaron: builtins.int
KEY_Lcedilla: builtins.int
KEY_Left: builtins.int
KEY_LightBulb: builtins.int
KEY_Linefeed: builtins.int
KEY_LiraSign: builtins.int
KEY_LogGrabInfo: builtins.int
KEY_LogOff: builtins.int
KEY_LogWindowTree: builtins.int
KEY_Lstroke: builtins.int
KEY_M: builtins.int
KEY_Mabovedot: builtins.int
KEY_Macedonia_DSE: builtins.int
KEY_Macedonia_GJE: builtins.int
KEY_Macedonia_KJE: builtins.int
KEY_Macedonia_dse: builtins.int
KEY_Macedonia_gje: builtins.int
KEY_Macedonia_kje: builtins.int
KEY_Mae_Koho: builtins.int
KEY_Mail: builtins.int
KEY_MailForward: builtins.int
KEY_Market: builtins.int
KEY_Massyo: builtins.int
KEY_Meeting: builtins.int
KEY_Memo: builtins.int
KEY_Menu: builtins.int
KEY_MenuKB: builtins.int
KEY_MenuPB: builtins.int
KEY_Messenger: builtins.int
KEY_Meta_L: builtins.int
KEY_Meta_R: builtins.int
KEY_MillSign: builtins.int
KEY_ModeLock: builtins.int
KEY_Mode_switch: builtins.int
KEY_MonBrightnessDown: builtins.int
KEY_MonBrightnessUp: builtins.int
KEY_MouseKeys_Accel_Enable: builtins.int
KEY_MouseKeys_Enable: builtins.int
KEY_Muhenkan: builtins.int
KEY_Multi_key: builtins.int
KEY_MultipleCandidate: builtins.int
KEY_Music: builtins.int
KEY_MyComputer: builtins.int
KEY_MySites: builtins.int
KEY_N: builtins.int
KEY_Nacute: builtins.int
KEY_NairaSign: builtins.int
KEY_Ncaron: builtins.int
KEY_Ncedilla: builtins.int
KEY_New: builtins.int
KEY_NewSheqelSign: builtins.int
KEY_News: builtins.int
KEY_Next: builtins.int
KEY_Next_VMode: builtins.int
KEY_Next_Virtual_Screen: builtins.int
KEY_Ntilde: builtins.int
KEY_Num_Lock: builtins.int
KEY_O: builtins.int
KEY_OE: builtins.int
KEY_Oacute: builtins.int
KEY_Obarred: builtins.int
KEY_Obelowdot: builtins.int
KEY_Ocaron: builtins.int
KEY_Ocircumflex: builtins.int
KEY_Ocircumflexacute: builtins.int
KEY_Ocircumflexbelowdot: builtins.int
KEY_Ocircumflexgrave: builtins.int
KEY_Ocircumflexhook: builtins.int
KEY_Ocircumflextilde: builtins.int
KEY_Odiaeresis: builtins.int
KEY_Odoubleacute: builtins.int
KEY_OfficeHome: builtins.int
KEY_Ograve: builtins.int
KEY_Ohook: builtins.int
KEY_Ohorn: builtins.int
KEY_Ohornacute: builtins.int
KEY_Ohornbelowdot: builtins.int
KEY_Ohorngrave: builtins.int
KEY_Ohornhook: builtins.int
KEY_Ohorntilde: builtins.int
KEY_Omacron: builtins.int
KEY_Ooblique: builtins.int
KEY_Open: builtins.int
KEY_OpenURL: builtins.int
KEY_Option: builtins.int
KEY_Oslash: builtins.int
KEY_Otilde: builtins.int
KEY_Overlay1_Enable: builtins.int
KEY_Overlay2_Enable: builtins.int
KEY_P: builtins.int
KEY_Pabovedot: builtins.int
KEY_Page_Down: builtins.int
KEY_Page_Up: builtins.int
KEY_Paste: builtins.int
KEY_Pause: builtins.int
KEY_PesetaSign: builtins.int
KEY_Phone: builtins.int
KEY_Pictures: builtins.int
KEY_Pointer_Accelerate: builtins.int
KEY_Pointer_Button1: builtins.int
KEY_Pointer_Button2: builtins.int
KEY_Pointer_Button3: builtins.int
KEY_Pointer_Button4: builtins.int
KEY_Pointer_Button5: builtins.int
KEY_Pointer_Button_Dflt: builtins.int
KEY_Pointer_DblClick1: builtins.int
KEY_Pointer_DblClick2: builtins.int
KEY_Pointer_DblClick3: builtins.int
KEY_Pointer_DblClick4: builtins.int
KEY_Pointer_DblClick5: builtins.int
KEY_Pointer_DblClick_Dflt: builtins.int
KEY_Pointer_DfltBtnNext: builtins.int
KEY_Pointer_DfltBtnPrev: builtins.int
KEY_Pointer_Down: builtins.int
KEY_Pointer_DownLeft: builtins.int
KEY_Pointer_DownRight: builtins.int
KEY_Pointer_Drag1: builtins.int
KEY_Pointer_Drag2: builtins.int
KEY_Pointer_Drag3: builtins.int
KEY_Pointer_Drag4: builtins.int
KEY_Pointer_Drag5: builtins.int
KEY_Pointer_Drag_Dflt: builtins.int
KEY_Pointer_EnableKeys: builtins.int
KEY_Pointer_Left: builtins.int
KEY_Pointer_Right: builtins.int
KEY_Pointer_Up: builtins.int
KEY_Pointer_UpLeft: builtins.int
KEY_Pointer_UpRight: builtins.int
KEY_PowerDown: builtins.int
KEY_PowerOff: builtins.int
KEY_Prev_VMode: builtins.int
KEY_Prev_Virtual_Screen: builtins.int
KEY_PreviousCandidate: builtins.int
KEY_Print: builtins.int
KEY_Prior: builtins.int
KEY_Q: builtins.int
KEY_R: builtins.int
KEY_R1: builtins.int
KEY_R10: builtins.int
KEY_R11: builtins.int
KEY_R12: builtins.int
KEY_R13: builtins.int
KEY_R14: builtins.int
KEY_R15: builtins.int
KEY_R2: builtins.int
KEY_R3: builtins.int
KEY_R4: builtins.int
KEY_R5: builtins.int
KEY_R6: builtins.int
KEY_R7: builtins.int
KEY_R8: builtins.int
KEY_R9: builtins.int
KEY_RFKill: builtins.int
KEY_Racute: builtins.int
KEY_Rcaron: builtins.int
KEY_Rcedilla: builtins.int
KEY_Red: builtins.int
KEY_Redo: builtins.int
KEY_Refresh: builtins.int
KEY_Reload: builtins.int
KEY_RepeatKeys_Enable: builtins.int
KEY_Reply: builtins.int
KEY_Return: builtins.int
KEY_Right: builtins.int
KEY_RockerDown: builtins.int
KEY_RockerEnter: builtins.int
KEY_RockerUp: builtins.int
KEY_Romaji: builtins.int
KEY_RotateWindows: builtins.int
KEY_RotationKB: builtins.int
KEY_RotationPB: builtins.int
KEY_RupeeSign: builtins.int
KEY_S: builtins.int
KEY_SCHWA: builtins.int
KEY_Sabovedot: builtins.int
KEY_Sacute: builtins.int
KEY_Save: builtins.int
KEY_Scaron: builtins.int
KEY_Scedilla: builtins.int
KEY_Scircumflex: builtins.int
KEY_ScreenSaver: builtins.int
KEY_ScrollClick: builtins.int
KEY_ScrollDown: builtins.int
KEY_ScrollUp: builtins.int
KEY_Scroll_Lock: builtins.int
KEY_Search: builtins.int
KEY_Select: builtins.int
KEY_SelectButton: builtins.int
KEY_Send: builtins.int
KEY_Serbian_DJE: builtins.int
KEY_Serbian_DZE: builtins.int
KEY_Serbian_JE: builtins.int
KEY_Serbian_LJE: builtins.int
KEY_Serbian_NJE: builtins.int
KEY_Serbian_TSHE: builtins.int
KEY_Serbian_dje: builtins.int
KEY_Serbian_dze: builtins.int
KEY_Serbian_je: builtins.int
KEY_Serbian_lje: builtins.int
KEY_Serbian_nje: builtins.int
KEY_Serbian_tshe: builtins.int
KEY_Shift_L: builtins.int
KEY_Shift_Lock: builtins.int
KEY_Shift_R: builtins.int
KEY_Shop: builtins.int
KEY_SingleCandidate: builtins.int
KEY_Sinh_a: builtins.int
KEY_Sinh_aa: builtins.int
KEY_Sinh_aa2: builtins.int
KEY_Sinh_ae: builtins.int
KEY_Sinh_ae2: builtins.int
KEY_Sinh_aee: builtins.int
KEY_Sinh_aee2: builtins.int
KEY_Sinh_ai: builtins.int
KEY_Sinh_ai2: builtins.int
KEY_Sinh_al: builtins.int
KEY_Sinh_au: builtins.int
KEY_Sinh_au2: builtins.int
KEY_Sinh_ba: builtins.int
KEY_Sinh_bha: builtins.int
KEY_Sinh_ca: builtins.int
KEY_Sinh_cha: builtins.int
KEY_Sinh_dda: builtins.int
KEY_Sinh_ddha: builtins.int
KEY_Sinh_dha: builtins.int
KEY_Sinh_dhha: builtins.int
KEY_Sinh_e: builtins.int
KEY_Sinh_e2: builtins.int
KEY_Sinh_ee: builtins.int
KEY_Sinh_ee2: builtins.int
KEY_Sinh_fa: builtins.int
KEY_Sinh_ga: builtins.int
KEY_Sinh_gha: builtins.int
KEY_Sinh_h2: builtins.int
KEY_Sinh_ha: builtins.int
KEY_Sinh_i: builtins.int
KEY_Sinh_i2: builtins.int
KEY_Sinh_ii: builtins.int
KEY_Sinh_ii2: builtins.int
KEY_Sinh_ja: builtins.int
KEY_Sinh_jha: builtins.int
KEY_Sinh_jnya: builtins.int
KEY_Sinh_ka: builtins.int
KEY_Sinh_kha: builtins.int
KEY_Sinh_kunddaliya: builtins.int
KEY_Sinh_la: builtins.int
KEY_Sinh_lla: builtins.int
KEY_Sinh_lu: builtins.int
KEY_Sinh_lu2: builtins.int
KEY_Sinh_luu: builtins.int
KEY_Sinh_luu2: builtins.int
KEY_Sinh_ma: builtins.int
KEY_Sinh_mba: builtins.int
KEY_Sinh_na: builtins.int
KEY_Sinh_ndda: builtins.int
KEY_Sinh_ndha: builtins.int
KEY_Sinh_ng: builtins.int
KEY_Sinh_ng2: builtins.int
KEY_Sinh_nga: builtins.int
KEY_Sinh_nja: builtins.int
KEY_Sinh_nna: builtins.int
KEY_Sinh_nya: builtins.int
KEY_Sinh_o: builtins.int
KEY_Sinh_o2: builtins.int
KEY_Sinh_oo: builtins.int
KEY_Sinh_oo2: builtins.int
KEY_Sinh_pa: builtins.int
KEY_Sinh_pha: builtins.int
KEY_Sinh_ra: builtins.int
KEY_Sinh_ri: builtins.int
KEY_Sinh_rii: builtins.int
KEY_Sinh_ru2: builtins.int
KEY_Sinh_ruu2: builtins.int
KEY_Sinh_sa: builtins.int
KEY_Sinh_sha: builtins.int
KEY_Sinh_ssha: builtins.int
KEY_Sinh_tha: builtins.int
KEY_Sinh_thha: builtins.int
KEY_Sinh_tta: builtins.int
KEY_Sinh_ttha: builtins.int
KEY_Sinh_u: builtins.int
KEY_Sinh_u2: builtins.int
KEY_Sinh_uu: builtins.int
KEY_Sinh_uu2: builtins.int
KEY_Sinh_va: builtins.int
KEY_Sinh_ya: builtins.int
KEY_Sleep: builtins.int
KEY_SlowKeys_Enable: builtins.int
KEY_Spell: builtins.int
KEY_SplitScreen: builtins.int
KEY_Standby: builtins.int
KEY_Start: builtins.int
KEY_StickyKeys_Enable: builtins.int
KEY_Stop: builtins.int
KEY_Subtitle: builtins.int
KEY_Super_L: builtins.int
KEY_Super_R: builtins.int
KEY_Support: builtins.int
KEY_Suspend: builtins.int
KEY_Switch_VT_1: builtins.int
KEY_Switch_VT_10: builtins.int
KEY_Switch_VT_11: builtins.int
KEY_Switch_VT_12: builtins.int
KEY_Switch_VT_2: builtins.int
KEY_Switch_VT_3: builtins.int
KEY_Switch_VT_4: builtins.int
KEY_Switch_VT_5: builtins.int
KEY_Switch_VT_6: builtins.int
KEY_Switch_VT_7: builtins.int
KEY_Switch_VT_8: builtins.int
KEY_Switch_VT_9: builtins.int
KEY_Sys_Req: builtins.int
KEY_T: builtins.int
KEY_THORN: builtins.int
KEY_Tab: builtins.int
KEY_Tabovedot: builtins.int
KEY_TaskPane: builtins.int
KEY_Tcaron: builtins.int
KEY_Tcedilla: builtins.int
KEY_Terminal: builtins.int
KEY_Terminate_Server: builtins.int
KEY_Thai_baht: builtins.int
KEY_Thai_bobaimai: builtins.int
KEY_Thai_chochan: builtins.int
KEY_Thai_chochang: builtins.int
KEY_Thai_choching: builtins.int
KEY_Thai_chochoe: builtins.int
KEY_Thai_dochada: builtins.int
KEY_Thai_dodek: builtins.int
KEY_Thai_fofa: builtins.int
KEY_Thai_fofan: builtins.int
KEY_Thai_hohip: builtins.int
KEY_Thai_honokhuk: builtins.int
KEY_Thai_khokhai: builtins.int
KEY_Thai_khokhon: builtins.int
KEY_Thai_khokhuat: builtins.int
KEY_Thai_khokhwai: builtins.int
KEY_Thai_khorakhang: builtins.int
KEY_Thai_kokai: builtins.int
KEY_Thai_lakkhangyao: builtins.int
KEY_Thai_lekchet: builtins.int
KEY_Thai_lekha: builtins.int
KEY_Thai_lekhok: builtins.int
KEY_Thai_lekkao: builtins.int
KEY_Thai_leknung: builtins.int
KEY_Thai_lekpaet: builtins.int
KEY_Thai_leksam: builtins.int
KEY_Thai_leksi: builtins.int
KEY_Thai_leksong: builtins.int
KEY_Thai_leksun: builtins.int
KEY_Thai_lochula: builtins.int
KEY_Thai_loling: builtins.int
KEY_Thai_lu: builtins.int
KEY_Thai_maichattawa: builtins.int
KEY_Thai_maiek: builtins.int
KEY_Thai_maihanakat: builtins.int
KEY_Thai_maihanakat_maitho: builtins.int
KEY_Thai_maitaikhu: builtins.int
KEY_Thai_maitho: builtins.int
KEY_Thai_maitri: builtins.int
KEY_Thai_maiyamok: builtins.int
KEY_Thai_moma: builtins.int
KEY_Thai_ngongu: builtins.int
KEY_Thai_nikhahit: builtins.int
KEY_Thai_nonen: builtins.int
KEY_Thai_nonu: builtins.int
KEY_Thai_oang: builtins.int
KEY_Thai_paiyannoi: builtins.int
KEY_Thai_phinthu: builtins.int
KEY_Thai_phophan: builtins.int
KEY_Thai_phophung: builtins.int
KEY_Thai_phosamphao: builtins.int
KEY_Thai_popla: builtins.int
KEY_Thai_rorua: builtins.int
KEY_Thai_ru: builtins.int
KEY_Thai_saraa: builtins.int
KEY_Thai_saraaa: builtins.int
KEY_Thai_saraae: builtins.int
KEY_Thai_saraaimaimalai: builtins.int
KEY_Thai_saraaimaimuan: builtins.int
KEY_Thai_saraam: builtins.int
KEY_Thai_sarae: builtins.int
KEY_Thai_sarai: builtins.int
KEY_Thai_saraii: builtins.int
KEY_Thai_sarao: builtins.int
KEY_Thai_sarau: builtins.int
KEY_Thai_saraue: builtins.int
KEY_Thai_sarauee: builtins.int
KEY_Thai_sarauu: builtins.int
KEY_Thai_sorusi: builtins.int
KEY_Thai_sosala: builtins.int
KEY_Thai_soso: builtins.int
KEY_Thai_sosua: builtins.int
KEY_Thai_thanthakhat: builtins.int
KEY_Thai_thonangmontho: builtins.int
KEY_Thai_thophuthao: builtins.int
KEY_Thai_thothahan: builtins.int
KEY_Thai_thothan: builtins.int
KEY_Thai_thothong: builtins.int
KEY_Thai_thothung: builtins.int
KEY_Thai_topatak: builtins.int
KEY_Thai_totao: builtins.int
KEY_Thai_wowaen: builtins.int
KEY_Thai_yoyak: builtins.int
KEY_Thai_yoying: builtins.int
KEY_Thorn: builtins.int
KEY_Time: builtins.int
KEY_ToDoList: builtins.int
KEY_Tools: builtins.int
KEY_TopMenu: builtins.int
KEY_TouchpadOff: builtins.int
KEY_TouchpadOn: builtins.int
KEY_TouchpadToggle: builtins.int
KEY_Touroku: builtins.int
KEY_Travel: builtins.int
KEY_Tslash: builtins.int
KEY_U: builtins.int
KEY_UWB: builtins.int
KEY_Uacute: builtins.int
KEY_Ubelowdot: builtins.int
KEY_Ubreve: builtins.int
KEY_Ucircumflex: builtins.int
KEY_Udiaeresis: builtins.int
KEY_Udoubleacute: builtins.int
KEY_Ugrave: builtins.int
KEY_Uhook: builtins.int
KEY_Uhorn: builtins.int
KEY_Uhornacute: builtins.int
KEY_Uhornbelowdot: builtins.int
KEY_Uhorngrave: builtins.int
KEY_Uhornhook: builtins.int
KEY_Uhorntilde: builtins.int
KEY_Ukrainian_GHE_WITH_UPTURN: builtins.int
KEY_Ukrainian_I: builtins.int
KEY_Ukrainian_IE: builtins.int
KEY_Ukrainian_YI: builtins.int
KEY_Ukrainian_ghe_with_upturn: builtins.int
KEY_Ukrainian_i: builtins.int
KEY_Ukrainian_ie: builtins.int
KEY_Ukrainian_yi: builtins.int
KEY_Ukranian_I: builtins.int
KEY_Ukranian_JE: builtins.int
KEY_Ukranian_YI: builtins.int
KEY_Ukranian_i: builtins.int
KEY_Ukranian_je: builtins.int
KEY_Ukranian_yi: builtins.int
KEY_Umacron: builtins.int
KEY_Undo: builtins.int
KEY_Ungrab: builtins.int
KEY_Uogonek: builtins.int
KEY_Up: builtins.int
KEY_Uring: builtins.int
KEY_User1KB: builtins.int
KEY_User2KB: builtins.int
KEY_UserPB: builtins.int
KEY_Utilde: builtins.int
KEY_V: builtins.int
KEY_VendorHome: builtins.int
KEY_Video: builtins.int
KEY_View: builtins.int
KEY_VoidSymbol: builtins.int
KEY_W: builtins.int
KEY_WLAN: builtins.int
KEY_WWAN: builtins.int
KEY_WWW: builtins.int
KEY_Wacute: builtins.int
KEY_WakeUp: builtins.int
KEY_Wcircumflex: builtins.int
KEY_Wdiaeresis: builtins.int
KEY_WebCam: builtins.int
KEY_Wgrave: builtins.int
KEY_WheelButton: builtins.int
KEY_WindowClear: builtins.int
KEY_WonSign: builtins.int
KEY_Word: builtins.int
KEY_X: builtins.int
KEY_Xabovedot: builtins.int
KEY_Xfer: builtins.int
KEY_Y: builtins.int
KEY_Yacute: builtins.int
KEY_Ybelowdot: builtins.int
KEY_Ycircumflex: builtins.int
KEY_Ydiaeresis: builtins.int
KEY_Yellow: builtins.int
KEY_Ygrave: builtins.int
KEY_Yhook: builtins.int
KEY_Ytilde: builtins.int
KEY_Z: builtins.int
KEY_Zabovedot: builtins.int
KEY_Zacute: builtins.int
KEY_Zcaron: builtins.int
KEY_Zen_Koho: builtins.int
KEY_Zenkaku: builtins.int
KEY_Zenkaku_Hankaku: builtins.int
KEY_ZoomIn: builtins.int
KEY_ZoomOut: builtins.int
KEY_Zstroke: builtins.int
KEY_a: builtins.int
KEY_aacute: builtins.int
KEY_abelowdot: builtins.int
KEY_abovedot: builtins.int
KEY_abreve: builtins.int
KEY_abreveacute: builtins.int
KEY_abrevebelowdot: builtins.int
KEY_abrevegrave: builtins.int
KEY_abrevehook: builtins.int
KEY_abrevetilde: builtins.int
KEY_acircumflex: builtins.int
KEY_acircumflexacute: builtins.int
KEY_acircumflexbelowdot: builtins.int
KEY_acircumflexgrave: builtins.int
KEY_acircumflexhook: builtins.int
KEY_acircumflextilde: builtins.int
KEY_acute: builtins.int
KEY_adiaeresis: builtins.int
KEY_ae: builtins.int
KEY_agrave: builtins.int
KEY_ahook: builtins.int
KEY_amacron: builtins.int
KEY_ampersand: builtins.int
KEY_aogonek: builtins.int
KEY_apostrophe: builtins.int
KEY_approxeq: builtins.int
KEY_approximate: builtins.int
KEY_aring: builtins.int
KEY_asciicircum: builtins.int
KEY_asciitilde: builtins.int
KEY_asterisk: builtins.int
KEY_at: builtins.int
KEY_atilde: builtins.int
KEY_b: builtins.int
KEY_babovedot: builtins.int
KEY_backslash: builtins.int
KEY_ballotcross: builtins.int
KEY_bar: builtins.int
KEY_because: builtins.int
KEY_blank: builtins.int
KEY_botintegral: builtins.int
KEY_botleftparens: builtins.int
KEY_botleftsqbracket: builtins.int
KEY_botleftsummation: builtins.int
KEY_botrightparens: builtins.int
KEY_botrightsqbracket: builtins.int
KEY_botrightsummation: builtins.int
KEY_bott: builtins.int
KEY_botvertsummationconnector: builtins.int
KEY_braceleft: builtins.int
KEY_braceright: builtins.int
KEY_bracketleft: builtins.int
KEY_bracketright: builtins.int
KEY_braille_blank: builtins.int
KEY_braille_dot_1: builtins.int
KEY_braille_dot_10: builtins.int
KEY_braille_dot_2: builtins.int
KEY_braille_dot_3: builtins.int
KEY_braille_dot_4: builtins.int
KEY_braille_dot_5: builtins.int
KEY_braille_dot_6: builtins.int
KEY_braille_dot_7: builtins.int
KEY_braille_dot_8: builtins.int
KEY_braille_dot_9: builtins.int
KEY_braille_dots_1: builtins.int
KEY_braille_dots_12: builtins.int
KEY_braille_dots_123: builtins.int
KEY_braille_dots_1234: builtins.int
KEY_braille_dots_12345: builtins.int
KEY_braille_dots_123456: builtins.int
KEY_braille_dots_1234567: builtins.int
KEY_braille_dots_12345678: builtins.int
KEY_braille_dots_1234568: builtins.int
KEY_braille_dots_123457: builtins.int
KEY_braille_dots_1234578: builtins.int
KEY_braille_dots_123458: builtins.int
KEY_braille_dots_12346: builtins.int
KEY_braille_dots_123467: builtins.int
KEY_braille_dots_1234678: builtins.int
KEY_braille_dots_123468: builtins.int
KEY_braille_dots_12347: builtins.int
KEY_braille_dots_123478: builtins.int
KEY_braille_dots_12348: builtins.int
KEY_braille_dots_1235: builtins.int
KEY_braille_dots_12356: builtins.int
KEY_braille_dots_123567: builtins.int
KEY_braille_dots_1235678: builtins.int
KEY_braille_dots_123568: builtins.int
KEY_braille_dots_12357: builtins.int
KEY_braille_dots_123578: builtins.int
KEY_braille_dots_12358: builtins.int
KEY_braille_dots_1236: builtins.int
KEY_braille_dots_12367: builtins.int
KEY_braille_dots_123678: builtins.int
KEY_braille_dots_12368: builtins.int
KEY_braille_dots_1237: builtins.int
KEY_braille_dots_12378: builtins.int
KEY_braille_dots_1238: builtins.int
KEY_braille_dots_124: builtins.int
KEY_braille_dots_1245: builtins.int
KEY_braille_dots_12456: builtins.int
KEY_braille_dots_124567: builtins.int
KEY_braille_dots_1245678: builtins.int
KEY_braille_dots_124568: builtins.int
KEY_braille_dots_12457: builtins.int
KEY_braille_dots_124578: builtins.int
KEY_braille_dots_12458: builtins.int
KEY_braille_dots_1246: builtins.int
KEY_braille_dots_12467: builtins.int
KEY_braille_dots_124678: builtins.int
KEY_braille_dots_12468: builtins.int
KEY_braille_dots_1247: builtins.int
KEY_braille_dots_12478: builtins.int
KEY_braille_dots_1248: builtins.int
KEY_braille_dots_125: builtins.int
KEY_braille_dots_1256: builtins.int
KEY_braille_dots_12567: builtins.int
KEY_braille_dots_125678: builtins.int
KEY_braille_dots_12568: builtins.int
KEY_braille_dots_1257: builtins.int
KEY_braille_dots_12578: builtins.int
KEY_braille_dots_1258: builtins.int
KEY_braille_dots_126: builtins.int
KEY_braille_dots_1267: builtins.int
KEY_braille_dots_12678: builtins.int
KEY_braille_dots_1268: builtins.int
KEY_braille_dots_127: builtins.int
KEY_braille_dots_1278: builtins.int
KEY_braille_dots_128: builtins.int
KEY_braille_dots_13: builtins.int
KEY_braille_dots_134: builtins.int
KEY_braille_dots_1345: builtins.int
KEY_braille_dots_13456: builtins.int
KEY_braille_dots_134567: builtins.int
KEY_braille_dots_1345678: builtins.int
KEY_braille_dots_134568: builtins.int
KEY_braille_dots_13457: builtins.int
KEY_braille_dots_134578: builtins.int
KEY_braille_dots_13458: builtins.int
KEY_braille_dots_1346: builtins.int
KEY_braille_dots_13467: builtins.int
KEY_braille_dots_134678: builtins.int
KEY_braille_dots_13468: builtins.int
KEY_braille_dots_1347: builtins.int
KEY_braille_dots_13478: builtins.int
KEY_braille_dots_1348: builtins.int
KEY_braille_dots_135: builtins.int
KEY_braille_dots_1356: builtins.int
KEY_braille_dots_13567: builtins.int
KEY_braille_dots_135678: builtins.int
KEY_braille_dots_13568: builtins.int
KEY_braille_dots_1357: builtins.int
KEY_braille_dots_13578: builtins.int
KEY_braille_dots_1358: builtins.int
KEY_braille_dots_136: builtins.int
KEY_braille_dots_1367: builtins.int
KEY_braille_dots_13678: builtins.int
KEY_braille_dots_1368: builtins.int
KEY_braille_dots_137: builtins.int
KEY_braille_dots_1378: builtins.int
KEY_braille_dots_138: builtins.int
KEY_braille_dots_14: builtins.int
KEY_braille_dots_145: builtins.int
KEY_braille_dots_1456: builtins.int
KEY_braille_dots_14567: builtins.int
KEY_braille_dots_145678: builtins.int
KEY_braille_dots_14568: builtins.int
KEY_braille_dots_1457: builtins.int
KEY_braille_dots_14578: builtins.int
KEY_braille_dots_1458: builtins.int
KEY_braille_dots_146: builtins.int
KEY_braille_dots_1467: builtins.int
KEY_braille_dots_14678: builtins.int
KEY_braille_dots_1468: builtins.int
KEY_braille_dots_147: builtins.int
KEY_braille_dots_1478: builtins.int
KEY_braille_dots_148: builtins.int
KEY_braille_dots_15: builtins.int
KEY_braille_dots_156: builtins.int
KEY_braille_dots_1567: builtins.int
KEY_braille_dots_15678: builtins.int
KEY_braille_dots_1568: builtins.int
KEY_braille_dots_157: builtins.int
KEY_braille_dots_1578: builtins.int
KEY_braille_dots_158: builtins.int
KEY_braille_dots_16: builtins.int
KEY_braille_dots_167: builtins.int
KEY_braille_dots_1678: builtins.int
KEY_braille_dots_168: builtins.int
KEY_braille_dots_17: builtins.int
KEY_braille_dots_178: builtins.int
KEY_braille_dots_18: builtins.int
KEY_braille_dots_2: builtins.int
KEY_braille_dots_23: builtins.int
KEY_braille_dots_234: builtins.int
KEY_braille_dots_2345: builtins.int
KEY_braille_dots_23456: builtins.int
KEY_braille_dots_234567: builtins.int
KEY_braille_dots_2345678: builtins.int
KEY_braille_dots_234568: builtins.int
KEY_braille_dots_23457: builtins.int
KEY_braille_dots_234578: builtins.int
KEY_braille_dots_23458: builtins.int
KEY_braille_dots_2346: builtins.int
KEY_braille_dots_23467: builtins.int
KEY_braille_dots_234678: builtins.int
KEY_braille_dots_23468: builtins.int
KEY_braille_dots_2347: builtins.int
KEY_braille_dots_23478: builtins.int
KEY_braille_dots_2348: builtins.int
KEY_braille_dots_235: builtins.int
KEY_braille_dots_2356: builtins.int
KEY_braille_dots_23567: builtins.int
KEY_braille_dots_235678: builtins.int
KEY_braille_dots_23568: builtins.int
KEY_braille_dots_2357: builtins.int
KEY_braille_dots_23578: builtins.int
KEY_braille_dots_2358: builtins.int
KEY_braille_dots_236: builtins.int
KEY_braille_dots_2367: builtins.int
KEY_braille_dots_23678: builtins.int
KEY_braille_dots_2368: builtins.int
KEY_braille_dots_237: builtins.int
KEY_braille_dots_2378: builtins.int
KEY_braille_dots_238: builtins.int
KEY_braille_dots_24: builtins.int
KEY_braille_dots_245: builtins.int
KEY_braille_dots_2456: builtins.int
KEY_braille_dots_24567: builtins.int
KEY_braille_dots_245678: builtins.int
KEY_braille_dots_24568: builtins.int
KEY_braille_dots_2457: builtins.int
KEY_braille_dots_24578: builtins.int
KEY_braille_dots_2458: builtins.int
KEY_braille_dots_246: builtins.int
KEY_braille_dots_2467: builtins.int
KEY_braille_dots_24678: builtins.int
KEY_braille_dots_2468: builtins.int
KEY_braille_dots_247: builtins.int
KEY_braille_dots_2478: builtins.int
KEY_braille_dots_248: builtins.int
KEY_braille_dots_25: builtins.int
KEY_braille_dots_256: builtins.int
KEY_braille_dots_2567: builtins.int
KEY_braille_dots_25678: builtins.int
KEY_braille_dots_2568: builtins.int
KEY_braille_dots_257: builtins.int
KEY_braille_dots_2578: builtins.int
KEY_braille_dots_258: builtins.int
KEY_braille_dots_26: builtins.int
KEY_braille_dots_267: builtins.int
KEY_braille_dots_2678: builtins.int
KEY_braille_dots_268: builtins.int
KEY_braille_dots_27: builtins.int
KEY_braille_dots_278: builtins.int
KEY_braille_dots_28: builtins.int
KEY_braille_dots_3: builtins.int
KEY_braille_dots_34: builtins.int
KEY_braille_dots_345: builtins.int
KEY_braille_dots_3456: builtins.int
KEY_braille_dots_34567: builtins.int
KEY_braille_dots_345678: builtins.int
KEY_braille_dots_34568: builtins.int
KEY_braille_dots_3457: builtins.int
KEY_braille_dots_34578: builtins.int
KEY_braille_dots_3458: builtins.int
KEY_braille_dots_346: builtins.int
KEY_braille_dots_3467: builtins.int
KEY_braille_dots_34678: builtins.int
KEY_braille_dots_3468: builtins.int
KEY_braille_dots_347: builtins.int
KEY_braille_dots_3478: builtins.int
KEY_braille_dots_348: builtins.int
KEY_braille_dots_35: builtins.int
KEY_braille_dots_356: builtins.int
KEY_braille_dots_3567: builtins.int
KEY_braille_dots_35678: builtins.int
KEY_braille_dots_3568: builtins.int
KEY_braille_dots_357: builtins.int
KEY_braille_dots_3578: builtins.int
KEY_braille_dots_358: builtins.int
KEY_braille_dots_36: builtins.int
KEY_braille_dots_367: builtins.int
KEY_braille_dots_3678: builtins.int
KEY_braille_dots_368: builtins.int
KEY_braille_dots_37: builtins.int
KEY_braille_dots_378: builtins.int
KEY_braille_dots_38: builtins.int
KEY_braille_dots_4: builtins.int
KEY_braille_dots_45: builtins.int
KEY_braille_dots_456: builtins.int
KEY_braille_dots_4567: builtins.int
KEY_braille_dots_45678: builtins.int
KEY_braille_dots_4568: builtins.int
KEY_braille_dots_457: builtins.int
KEY_braille_dots_4578: builtins.int
KEY_braille_dots_458: builtins.int
KEY_braille_dots_46: builtins.int
KEY_braille_dots_467: builtins.int
KEY_braille_dots_4678: builtins.int
KEY_braille_dots_468: builtins.int
KEY_braille_dots_47: builtins.int
KEY_braille_dots_478: builtins.int
KEY_braille_dots_48: builtins.int
KEY_braille_dots_5: builtins.int
KEY_braille_dots_56: builtins.int
KEY_braille_dots_567: builtins.int
KEY_braille_dots_5678: builtins.int
KEY_braille_dots_568: builtins.int
KEY_braille_dots_57: builtins.int
KEY_braille_dots_578: builtins.int
KEY_braille_dots_58: builtins.int
KEY_braille_dots_6: builtins.int
KEY_braille_dots_67: builtins.int
KEY_braille_dots_678: builtins.int
KEY_braille_dots_68: builtins.int
KEY_braille_dots_7: builtins.int
KEY_braille_dots_78: builtins.int
KEY_braille_dots_8: builtins.int
KEY_breve: builtins.int
KEY_brokenbar: builtins.int
KEY_c: builtins.int
KEY_c_h: builtins.int
KEY_cabovedot: builtins.int
KEY_cacute: builtins.int
KEY_careof: builtins.int
KEY_caret: builtins.int
KEY_caron: builtins.int
KEY_ccaron: builtins.int
KEY_ccedilla: builtins.int
KEY_ccircumflex: builtins.int
KEY_cedilla: builtins.int
KEY_cent: builtins.int
KEY_ch: builtins.int
KEY_checkerboard: builtins.int
KEY_checkmark: builtins.int
KEY_circle: builtins.int
KEY_club: builtins.int
KEY_colon: builtins.int
KEY_comma: builtins.int
KEY_containsas: builtins.int
KEY_copyright: builtins.int
KEY_cr: builtins.int
KEY_crossinglines: builtins.int
KEY_cuberoot: builtins.int
KEY_currency: builtins.int
KEY_cursor: builtins.int
KEY_d: builtins.int
KEY_dabovedot: builtins.int
KEY_dagger: builtins.int
KEY_dcaron: builtins.int
KEY_dead_A: builtins.int
KEY_dead_E: builtins.int
KEY_dead_I: builtins.int
KEY_dead_O: builtins.int
KEY_dead_U: builtins.int
KEY_dead_a: builtins.int
KEY_dead_abovecomma: builtins.int
KEY_dead_abovedot: builtins.int
KEY_dead_abovereversedcomma: builtins.int
KEY_dead_abovering: builtins.int
KEY_dead_aboveverticalline: builtins.int
KEY_dead_acute: builtins.int
KEY_dead_belowbreve: builtins.int
KEY_dead_belowcircumflex: builtins.int
KEY_dead_belowcomma: builtins.int
KEY_dead_belowdiaeresis: builtins.int
KEY_dead_belowdot: builtins.int
KEY_dead_belowmacron: builtins.int
KEY_dead_belowring: builtins.int
KEY_dead_belowtilde: builtins.int
KEY_dead_belowverticalline: builtins.int
KEY_dead_breve: builtins.int
KEY_dead_capital_schwa: builtins.int
KEY_dead_caron: builtins.int
KEY_dead_cedilla: builtins.int
KEY_dead_circumflex: builtins.int
KEY_dead_currency: builtins.int
KEY_dead_dasia: builtins.int
KEY_dead_diaeresis: builtins.int
KEY_dead_doubleacute: builtins.int
KEY_dead_doublegrave: builtins.int
KEY_dead_e: builtins.int
KEY_dead_grave: builtins.int
KEY_dead_greek: builtins.int
KEY_dead_hook: builtins.int
KEY_dead_horn: builtins.int
KEY_dead_i: builtins.int
KEY_dead_invertedbreve: builtins.int
KEY_dead_iota: builtins.int
KEY_dead_longsolidusoverlay: builtins.int
KEY_dead_lowline: builtins.int
KEY_dead_macron: builtins.int
KEY_dead_o: builtins.int
KEY_dead_ogonek: builtins.int
KEY_dead_perispomeni: builtins.int
KEY_dead_psili: builtins.int
KEY_dead_semivoiced_sound: builtins.int
KEY_dead_small_schwa: builtins.int
KEY_dead_stroke: builtins.int
KEY_dead_tilde: builtins.int
KEY_dead_u: builtins.int
KEY_dead_voiced_sound: builtins.int
KEY_decimalpoint: builtins.int
KEY_degree: builtins.int
KEY_diaeresis: builtins.int
KEY_diamond: builtins.int
KEY_digitspace: builtins.int
KEY_dintegral: builtins.int
KEY_division: builtins.int
KEY_dollar: builtins.int
KEY_doubbaselinedot: builtins.int
KEY_doubleacute: builtins.int
KEY_doubledagger: builtins.int
KEY_doublelowquotemark: builtins.int
KEY_downarrow: builtins.int
KEY_downcaret: builtins.int
KEY_downshoe: builtins.int
KEY_downstile: builtins.int
KEY_downtack: builtins.int
KEY_dstroke: builtins.int
KEY_e: builtins.int
KEY_eabovedot: builtins.int
KEY_eacute: builtins.int
KEY_ebelowdot: builtins.int
KEY_ecaron: builtins.int
KEY_ecircumflex: builtins.int
KEY_ecircumflexacute: builtins.int
KEY_ecircumflexbelowdot: builtins.int
KEY_ecircumflexgrave: builtins.int
KEY_ecircumflexhook: builtins.int
KEY_ecircumflextilde: builtins.int
KEY_ediaeresis: builtins.int
KEY_egrave: builtins.int
KEY_ehook: builtins.int
KEY_eightsubscript: builtins.int
KEY_eightsuperior: builtins.int
KEY_elementof: builtins.int
KEY_ellipsis: builtins.int
KEY_em3space: builtins.int
KEY_em4space: builtins.int
KEY_emacron: builtins.int
KEY_emdash: builtins.int
KEY_emfilledcircle: builtins.int
KEY_emfilledrect: builtins.int
KEY_emopencircle: builtins.int
KEY_emopenrectangle: builtins.int
KEY_emptyset: builtins.int
KEY_emspace: builtins.int
KEY_endash: builtins.int
KEY_enfilledcircbullet: builtins.int
KEY_enfilledsqbullet: builtins.int
KEY_eng: builtins.int
KEY_enopencircbullet: builtins.int
KEY_enopensquarebullet: builtins.int
KEY_enspace: builtins.int
KEY_eogonek: builtins.int
KEY_equal: builtins.int
KEY_eth: builtins.int
KEY_etilde: builtins.int
KEY_exclam: builtins.int
KEY_exclamdown: builtins.int
KEY_ezh: builtins.int
KEY_f: builtins.int
KEY_fabovedot: builtins.int
KEY_femalesymbol: builtins.int
KEY_ff: builtins.int
KEY_figdash: builtins.int
KEY_filledlefttribullet: builtins.int
KEY_filledrectbullet: builtins.int
KEY_filledrighttribullet: builtins.int
KEY_filledtribulletdown: builtins.int
KEY_filledtribulletup: builtins.int
KEY_fiveeighths: builtins.int
KEY_fivesixths: builtins.int
KEY_fivesubscript: builtins.int
KEY_fivesuperior: builtins.int
KEY_fourfifths: builtins.int
KEY_foursubscript: builtins.int
KEY_foursuperior: builtins.int
KEY_fourthroot: builtins.int
KEY_function: builtins.int
KEY_g: builtins.int
KEY_gabovedot: builtins.int
KEY_gbreve: builtins.int
KEY_gcaron: builtins.int
KEY_gcedilla: builtins.int
KEY_gcircumflex: builtins.int
KEY_grave: builtins.int
KEY_greater: builtins.int
KEY_greaterthanequal: builtins.int
KEY_guillemotleft: builtins.int
KEY_guillemotright: builtins.int
KEY_h: builtins.int
KEY_hairspace: builtins.int
KEY_hcircumflex: builtins.int
KEY_heart: builtins.int
KEY_hebrew_aleph: builtins.int
KEY_hebrew_ayin: builtins.int
KEY_hebrew_bet: builtins.int
KEY_hebrew_beth: builtins.int
KEY_hebrew_chet: builtins.int
KEY_hebrew_dalet: builtins.int
KEY_hebrew_daleth: builtins.int
KEY_hebrew_doublelowline: builtins.int
KEY_hebrew_finalkaph: builtins.int
KEY_hebrew_finalmem: builtins.int
KEY_hebrew_finalnun: builtins.int
KEY_hebrew_finalpe: builtins.int
KEY_hebrew_finalzade: builtins.int
KEY_hebrew_finalzadi: builtins.int
KEY_hebrew_gimel: builtins.int
KEY_hebrew_gimmel: builtins.int
KEY_hebrew_he: builtins.int
KEY_hebrew_het: builtins.int
KEY_hebrew_kaph: builtins.int
KEY_hebrew_kuf: builtins.int
KEY_hebrew_lamed: builtins.int
KEY_hebrew_mem: builtins.int
KEY_hebrew_nun: builtins.int
KEY_hebrew_pe: builtins.int
KEY_hebrew_qoph: builtins.int
KEY_hebrew_resh: builtins.int
KEY_hebrew_samech: builtins.int
KEY_hebrew_samekh: builtins.int
KEY_hebrew_shin: builtins.int
KEY_hebrew_taf: builtins.int
KEY_hebrew_taw: builtins.int
KEY_hebrew_tet: builtins.int
KEY_hebrew_teth: builtins.int
KEY_hebrew_waw: builtins.int
KEY_hebrew_yod: builtins.int
KEY_hebrew_zade: builtins.int
KEY_hebrew_zadi: builtins.int
KEY_hebrew_zain: builtins.int
KEY_hebrew_zayin: builtins.int
KEY_hexagram: builtins.int
KEY_horizconnector: builtins.int
KEY_horizlinescan1: builtins.int
KEY_horizlinescan3: builtins.int
KEY_horizlinescan5: builtins.int
KEY_horizlinescan7: builtins.int
KEY_horizlinescan9: builtins.int
KEY_hstroke: builtins.int
KEY_ht: builtins.int
KEY_hyphen: builtins.int
KEY_i: builtins.int
KEY_iTouch: builtins.int
KEY_iacute: builtins.int
KEY_ibelowdot: builtins.int
KEY_ibreve: builtins.int
KEY_icircumflex: builtins.int
KEY_identical: builtins.int
KEY_idiaeresis: builtins.int
KEY_idotless: builtins.int
KEY_ifonlyif: builtins.int
KEY_igrave: builtins.int
KEY_ihook: builtins.int
KEY_imacron: builtins.int
KEY_implies: builtins.int
KEY_includedin: builtins.int
KEY_includes: builtins.int
KEY_infinity: builtins.int
KEY_integral: builtins.int
KEY_intersection: builtins.int
KEY_iogonek: builtins.int
KEY_itilde: builtins.int
KEY_j: builtins.int
KEY_jcircumflex: builtins.int
KEY_jot: builtins.int
KEY_k: builtins.int
KEY_kana_A: builtins.int
KEY_kana_CHI: builtins.int
KEY_kana_E: builtins.int
KEY_kana_FU: builtins.int
KEY_kana_HA: builtins.int
KEY_kana_HE: builtins.int
KEY_kana_HI: builtins.int
KEY_kana_HO: builtins.int
KEY_kana_HU: builtins.int
KEY_kana_I: builtins.int
KEY_kana_KA: builtins.int
KEY_kana_KE: builtins.int
KEY_kana_KI: builtins.int
KEY_kana_KO: builtins.int
KEY_kana_KU: builtins.int
KEY_kana_MA: builtins.int
KEY_kana_ME: builtins.int
KEY_kana_MI: builtins.int
KEY_kana_MO: builtins.int
KEY_kana_MU: builtins.int
KEY_kana_N: builtins.int
KEY_kana_NA: builtins.int
KEY_kana_NE: builtins.int
KEY_kana_NI: builtins.int
KEY_kana_NO: builtins.int
KEY_kana_NU: builtins.int
KEY_kana_O: builtins.int
KEY_kana_RA: builtins.int
KEY_kana_RE: builtins.int
KEY_kana_RI: builtins.int
KEY_kana_RO: builtins.int
KEY_kana_RU: builtins.int
KEY_kana_SA: builtins.int
KEY_kana_SE: builtins.int
KEY_kana_SHI: builtins.int
KEY_kana_SO: builtins.int
KEY_kana_SU: builtins.int
KEY_kana_TA: builtins.int
KEY_kana_TE: builtins.int
KEY_kana_TI: builtins.int
KEY_kana_TO: builtins.int
KEY_kana_TSU: builtins.int
KEY_kana_TU: builtins.int
KEY_kana_U: builtins.int
KEY_kana_WA: builtins.int
KEY_kana_WO: builtins.int
KEY_kana_YA: builtins.int
KEY_kana_YO: builtins.int
KEY_kana_YU: builtins.int
KEY_kana_a: builtins.int
KEY_kana_closingbracket: builtins.int
KEY_kana_comma: builtins.int
KEY_kana_conjunctive: builtins.int
KEY_kana_e: builtins.int
KEY_kana_fullstop: builtins.int
KEY_kana_i: builtins.int
KEY_kana_middledot: builtins.int
KEY_kana_o: builtins.int
KEY_kana_openingbracket: builtins.int
KEY_kana_switch: builtins.int
KEY_kana_tsu: builtins.int
KEY_kana_tu: builtins.int
KEY_kana_u: builtins.int
KEY_kana_ya: builtins.int
KEY_kana_yo: builtins.int
KEY_kana_yu: builtins.int
KEY_kappa: builtins.int
KEY_kcedilla: builtins.int
KEY_kra: builtins.int
KEY_l: builtins.int
KEY_lacute: builtins.int
KEY_latincross: builtins.int
KEY_lbelowdot: builtins.int
KEY_lcaron: builtins.int
KEY_lcedilla: builtins.int
KEY_leftanglebracket: builtins.int
KEY_leftarrow: builtins.int
KEY_leftcaret: builtins.int
KEY_leftdoublequotemark: builtins.int
KEY_leftmiddlecurlybrace: builtins.int
KEY_leftopentriangle: builtins.int
KEY_leftpointer: builtins.int
KEY_leftradical: builtins.int
KEY_leftshoe: builtins.int
KEY_leftsinglequotemark: builtins.int
KEY_leftt: builtins.int
KEY_lefttack: builtins.int
KEY_less: builtins.int
KEY_lessthanequal: builtins.int
KEY_lf: builtins.int
KEY_logicaland: builtins.int
KEY_logicalor: builtins.int
KEY_lowleftcorner: builtins.int
KEY_lowrightcorner: builtins.int
KEY_lstroke: builtins.int
KEY_m: builtins.int
KEY_mabovedot: builtins.int
KEY_macron: builtins.int
KEY_malesymbol: builtins.int
KEY_maltesecross: builtins.int
KEY_marker: builtins.int
KEY_masculine: builtins.int
KEY_minus: builtins.int
KEY_minutes: builtins.int
KEY_mu: builtins.int
KEY_multiply: builtins.int
KEY_musicalflat: builtins.int
KEY_musicalsharp: builtins.int
KEY_n: builtins.int
KEY_nabla: builtins.int
KEY_nacute: builtins.int
KEY_ncaron: builtins.int
KEY_ncedilla: builtins.int
KEY_ninesubscript: builtins.int
KEY_ninesuperior: builtins.int
KEY_nl: builtins.int
KEY_nobreakspace: builtins.int
KEY_notapproxeq: builtins.int
KEY_notelementof: builtins.int
KEY_notequal: builtins.int
KEY_notidentical: builtins.int
KEY_notsign: builtins.int
KEY_ntilde: builtins.int
KEY_numbersign: builtins.int
KEY_numerosign: builtins.int
KEY_o: builtins.int
KEY_oacute: builtins.int
KEY_obarred: builtins.int
KEY_obelowdot: builtins.int
KEY_ocaron: builtins.int
KEY_ocircumflex: builtins.int
KEY_ocircumflexacute: builtins.int
KEY_ocircumflexbelowdot: builtins.int
KEY_ocircumflexgrave: builtins.int
KEY_ocircumflexhook: builtins.int
KEY_ocircumflextilde: builtins.int
KEY_odiaeresis: builtins.int
KEY_odoubleacute: builtins.int
KEY_oe: builtins.int
KEY_ogonek: builtins.int
KEY_ograve: builtins.int
KEY_ohook: builtins.int
KEY_ohorn: builtins.int
KEY_ohornacute: builtins.int
KEY_ohornbelowdot: builtins.int
KEY_ohorngrave: builtins.int
KEY_ohornhook: builtins.int
KEY_ohorntilde: builtins.int
KEY_omacron: builtins.int
KEY_oneeighth: builtins.int
KEY_onefifth: builtins.int
KEY_onehalf: builtins.int
KEY_onequarter: builtins.int
KEY_onesixth: builtins.int
KEY_onesubscript: builtins.int
KEY_onesuperior: builtins.int
KEY_onethird: builtins.int
KEY_ooblique: builtins.int
KEY_openrectbullet: builtins.int
KEY_openstar: builtins.int
KEY_opentribulletdown: builtins.int
KEY_opentribulletup: builtins.int
KEY_ordfeminine: builtins.int
KEY_oslash: builtins.int
KEY_otilde: builtins.int
KEY_overbar: builtins.int
KEY_overline: builtins.int
KEY_p: builtins.int
KEY_pabovedot: builtins.int
KEY_paragraph: builtins.int
KEY_parenleft: builtins.int
KEY_parenright: builtins.int
KEY_partdifferential: builtins.int
KEY_partialderivative: builtins.int
KEY_percent: builtins.int
KEY_period: builtins.int
KEY_periodcentered: builtins.int
KEY_permille: builtins.int
KEY_phonographcopyright: builtins.int
KEY_plus: builtins.int
KEY_plusminus: builtins.int
KEY_prescription: builtins.int
KEY_prolongedsound: builtins.int
KEY_punctspace: builtins.int
KEY_q: builtins.int
KEY_quad: builtins.int
KEY_question: builtins.int
KEY_questiondown: builtins.int
KEY_quotedbl: builtins.int
KEY_quoteleft: builtins.int
KEY_quoteright: builtins.int
KEY_r: builtins.int
KEY_racute: builtins.int
KEY_radical: builtins.int
KEY_rcaron: builtins.int
KEY_rcedilla: builtins.int
KEY_registered: builtins.int
KEY_rightanglebracket: builtins.int
KEY_rightarrow: builtins.int
KEY_rightcaret: builtins.int
KEY_rightdoublequotemark: builtins.int
KEY_rightmiddlecurlybrace: builtins.int
KEY_rightmiddlesummation: builtins.int
KEY_rightopentriangle: builtins.int
KEY_rightpointer: builtins.int
KEY_rightshoe: builtins.int
KEY_rightsinglequotemark: builtins.int
KEY_rightt: builtins.int
KEY_righttack: builtins.int
KEY_s: builtins.int
KEY_sabovedot: builtins.int
KEY_sacute: builtins.int
KEY_scaron: builtins.int
KEY_scedilla: builtins.int
KEY_schwa: builtins.int
KEY_scircumflex: builtins.int
KEY_script_switch: builtins.int
KEY_seconds: builtins.int
KEY_section: builtins.int
KEY_semicolon: builtins.int
KEY_semivoicedsound: builtins.int
KEY_seveneighths: builtins.int
KEY_sevensubscript: builtins.int
KEY_sevensuperior: builtins.int
KEY_signaturemark: builtins.int
KEY_signifblank: builtins.int
KEY_similarequal: builtins.int
KEY_singlelowquotemark: builtins.int
KEY_sixsubscript: builtins.int
KEY_sixsuperior: builtins.int
KEY_slash: builtins.int
KEY_soliddiamond: builtins.int
KEY_space: builtins.int
KEY_squareroot: builtins.int
KEY_ssharp: builtins.int
KEY_sterling: builtins.int
KEY_stricteq: builtins.int
KEY_t: builtins.int
KEY_tabovedot: builtins.int
KEY_tcaron: builtins.int
KEY_tcedilla: builtins.int
KEY_telephone: builtins.int
KEY_telephonerecorder: builtins.int
KEY_therefore: builtins.int
KEY_thinspace: builtins.int
KEY_thorn: builtins.int
KEY_threeeighths: builtins.int
KEY_threefifths: builtins.int
KEY_threequarters: builtins.int
KEY_threesubscript: builtins.int
KEY_threesuperior: builtins.int
KEY_tintegral: builtins.int
KEY_topintegral: builtins.int
KEY_topleftparens: builtins.int
KEY_topleftradical: builtins.int
KEY_topleftsqbracket: builtins.int
KEY_topleftsummation: builtins.int
KEY_toprightparens: builtins.int
KEY_toprightsqbracket: builtins.int
KEY_toprightsummation: builtins.int
KEY_topt: builtins.int
KEY_topvertsummationconnector: builtins.int
KEY_trademark: builtins.int
KEY_trademarkincircle: builtins.int
KEY_tslash: builtins.int
KEY_twofifths: builtins.int
KEY_twosubscript: builtins.int
KEY_twosuperior: builtins.int
KEY_twothirds: builtins.int
KEY_u: builtins.int
KEY_uacute: builtins.int
KEY_ubelowdot: builtins.int
KEY_ubreve: builtins.int
KEY_ucircumflex: builtins.int
KEY_udiaeresis: builtins.int
KEY_udoubleacute: builtins.int
KEY_ugrave: builtins.int
KEY_uhook: builtins.int
KEY_uhorn: builtins.int
KEY_uhornacute: builtins.int
KEY_uhornbelowdot: builtins.int
KEY_uhorngrave: builtins.int
KEY_uhornhook: builtins.int
KEY_uhorntilde: builtins.int
KEY_umacron: builtins.int
KEY_underbar: builtins.int
KEY_underscore: builtins.int
KEY_union: builtins.int
KEY_uogonek: builtins.int
KEY_uparrow: builtins.int
KEY_upcaret: builtins.int
KEY_upleftcorner: builtins.int
KEY_uprightcorner: builtins.int
KEY_upshoe: builtins.int
KEY_upstile: builtins.int
KEY_uptack: builtins.int
KEY_uring: builtins.int
KEY_utilde: builtins.int
KEY_v: builtins.int
KEY_variation: builtins.int
KEY_vertbar: builtins.int
KEY_vertconnector: builtins.int
KEY_voicedsound: builtins.int
KEY_vt: builtins.int
KEY_w: builtins.int
KEY_wacute: builtins.int
KEY_wcircumflex: builtins.int
KEY_wdiaeresis: builtins.int
KEY_wgrave: builtins.int
KEY_x: builtins.int
KEY_xabovedot: builtins.int
KEY_y: builtins.int
KEY_yacute: builtins.int
KEY_ybelowdot: builtins.int
KEY_ycircumflex: builtins.int
KEY_ydiaeresis: builtins.int
KEY_yen: builtins.int
KEY_ygrave: builtins.int
KEY_yhook: builtins.int
KEY_ytilde: builtins.int
KEY_z: builtins.int
KEY_zabovedot: builtins.int
KEY_zacute: builtins.int
KEY_zcaron: builtins.int
KEY_zerosubscript: builtins.int
KEY_zerosuperior: builtins.int
KEY_zstroke: builtins.int
MAJOR_VERSION: builtins.int
MAX_TIMECOORD_AXES: builtins.int
MICRO_VERSION: builtins.int
MINOR_VERSION: builtins.int
PARENT_RELATIVE: builtins.int
PRIORITY_REDRAW: builtins.int
SELECTION_CLIPBOARD: Atom
SELECTION_PRIMARY: Atom
SELECTION_SECONDARY: Atom
SELECTION_TYPE_ATOM: Atom
SELECTION_TYPE_BITMAP: Atom
SELECTION_TYPE_COLORMAP: Atom
SELECTION_TYPE_DRAWABLE: Atom
SELECTION_TYPE_INTEGER: Atom
SELECTION_TYPE_PIXMAP: Atom
SELECTION_TYPE_STRING: Atom
SELECTION_TYPE_WINDOW: Atom
TARGET_BITMAP: Atom
TARGET_COLORMAP: Atom
TARGET_DRAWABLE: Atom
TARGET_PIXMAP: Atom
TARGET_STRING: Atom
