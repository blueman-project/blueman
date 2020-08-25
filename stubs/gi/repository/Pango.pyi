import builtins
import typing

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import HarfBuzz
from gi.repository import cairo


class Context(GObject.Object):

    def changed(self) -> None: ...

    def get_base_dir(self) -> Direction: ...

    def get_base_gravity(self) -> Gravity: ...

    def get_font_description(self) -> FontDescription: ...

    def get_font_map(self) -> FontMap: ...

    def get_gravity(self) -> Gravity: ...

    def get_gravity_hint(self) -> GravityHint: ...

    def get_language(self) -> Language: ...

    def get_matrix(self) -> typing.Optional[Matrix]: ...

    def get_metrics(self, desc: typing.Optional[FontDescription], language: typing.Optional[Language]) -> FontMetrics: ...

    def get_round_glyph_positions(self) -> builtins.bool: ...

    def get_serial(self) -> builtins.int: ...

    def list_families(self) -> typing.Sequence[FontFamily]: ...

    def load_font(self, desc: FontDescription) -> typing.Optional[Font]: ...

    def load_fontset(self, desc: FontDescription, language: Language) -> typing.Optional[Fontset]: ...

    @staticmethod
    def new(**kwargs) -> Context: ...  # type: ignore

    def set_base_dir(self, direction: Direction) -> None: ...

    def set_base_gravity(self, gravity: Gravity) -> None: ...

    def set_font_description(self, desc: FontDescription) -> None: ...

    def set_font_map(self, font_map: FontMap) -> None: ...

    def set_gravity_hint(self, hint: GravityHint) -> None: ...

    def set_language(self, language: Language) -> None: ...

    def set_matrix(self, matrix: typing.Optional[Matrix]) -> None: ...

    def set_round_glyph_positions(self, round_positions: builtins.bool) -> None: ...


class Coverage(GObject.Object):

    def copy(self) -> Coverage: ...

    @staticmethod
    def from_bytes(bytes: builtins.bytes) -> typing.Optional[Coverage]: ...

    def get(self, index_: builtins.int) -> CoverageLevel: ...

    def max(self, other: Coverage) -> None: ...

    @staticmethod
    def new(**kwargs) -> Coverage: ...  # type: ignore

    def ref(self) -> Coverage: ...

    def set(self, index_: builtins.int, level: CoverageLevel) -> None: ...

    def to_bytes(self) -> builtins.bytes: ...

    def unref(self) -> None: ...


class Engine(GObject.Object):
    parent_instance: GObject.Object


class Font(GObject.Object):
    parent_instance: GObject.Object

    def describe(self) -> FontDescription: ...

    def describe_with_absolute_size(self) -> FontDescription: ...

    @staticmethod
    def descriptions_free(descs: typing.Optional[typing.Sequence[FontDescription]]) -> None: ...

    def find_shaper(self, language: Language, ch: builtins.int) -> EngineShape: ...

    def get_coverage(self, language: Language) -> Coverage: ...

    def get_face(self) -> FontFace: ...

    def get_features(self, num_features: builtins.int) -> typing.Tuple[typing.Sequence[HarfBuzz.feature_t], builtins.int]: ...

    def get_font_map(self) -> typing.Optional[FontMap]: ...

    def get_glyph_extents(self, glyph: builtins.int) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_metrics(self, language: typing.Optional[Language]) -> FontMetrics: ...

    def has_char(self, wc: builtins.str) -> builtins.bool: ...

    def do_create_hb_font(self) -> HarfBuzz.font_t: ...

    def do_describe(self) -> FontDescription: ...

    def do_describe_absolute(self) -> FontDescription: ...

    def do_get_coverage(self, language: Language) -> Coverage: ...

    def do_get_features(self, num_features: builtins.int) -> typing.Tuple[typing.Sequence[HarfBuzz.feature_t], builtins.int]: ...

    def do_get_font_map(self) -> typing.Optional[FontMap]: ...

    def do_get_glyph_extents(self, glyph: builtins.int) -> typing.Tuple[Rectangle, Rectangle]: ...

    def do_get_metrics(self, language: typing.Optional[Language]) -> FontMetrics: ...


class FontFace(GObject.Object):
    parent_instance: GObject.Object

    def describe(self) -> FontDescription: ...

    def get_face_name(self) -> builtins.str: ...

    def get_family(self) -> FontFamily: ...

    def is_synthesized(self) -> builtins.bool: ...

    def list_sizes(self) -> typing.Sequence[builtins.int]: ...

    def do_describe(self) -> FontDescription: ...

    def do_get_face_name(self) -> builtins.str: ...

    def do_get_family(self) -> FontFamily: ...

    def do_is_synthesized(self) -> builtins.bool: ...

    def do_list_sizes(self) -> typing.Sequence[builtins.int]: ...


class FontFamily(GObject.Object):
    parent_instance: GObject.Object

    def get_face(self, name: typing.Optional[builtins.str]) -> typing.Optional[FontFace]: ...

    def get_name(self) -> builtins.str: ...

    def is_monospace(self) -> builtins.bool: ...

    def is_variable(self) -> builtins.bool: ...

    def list_faces(self) -> typing.Sequence[FontFace]: ...

    def do_get_face(self, name: typing.Optional[builtins.str]) -> typing.Optional[FontFace]: ...

    def do_get_name(self) -> builtins.str: ...

    def do_is_monospace(self) -> builtins.bool: ...

    def do_is_variable(self) -> builtins.bool: ...

    def do_list_faces(self) -> typing.Sequence[FontFace]: ...


class FontMap(GObject.Object):
    parent_instance: GObject.Object

    def changed(self) -> None: ...

    def create_context(self) -> Context: ...

    def get_family(self, name: builtins.str) -> FontFamily: ...

    def get_serial(self) -> builtins.int: ...

    def list_families(self) -> typing.Sequence[FontFamily]: ...

    def load_font(self, context: Context, desc: FontDescription) -> typing.Optional[Font]: ...

    def load_fontset(self, context: Context, desc: FontDescription, language: Language) -> typing.Optional[Fontset]: ...

    def do_changed(self) -> None: ...

    def do_get_family(self, name: builtins.str) -> FontFamily: ...

    def do_get_serial(self) -> builtins.int: ...

    def do_list_families(self) -> typing.Sequence[FontFamily]: ...

    def do_load_font(self, context: Context, desc: FontDescription) -> typing.Optional[Font]: ...

    def do_load_fontset(self, context: Context, desc: FontDescription, language: Language) -> typing.Optional[Fontset]: ...


class Fontset(GObject.Object):
    parent_instance: GObject.Object

    def foreach(self, func: FontsetForeachFunc, *data: typing.Optional[builtins.object]) -> None: ...

    def get_font(self, wc: builtins.int) -> Font: ...

    def get_metrics(self) -> FontMetrics: ...

    def do_foreach(self, func: FontsetForeachFunc, data: typing.Optional[builtins.object]) -> None: ...

    def do_get_font(self, wc: builtins.int) -> Font: ...

    def do_get_language(self) -> Language: ...

    def do_get_metrics(self) -> FontMetrics: ...


class Layout(GObject.Object):

    def context_changed(self) -> None: ...

    def copy(self) -> Layout: ...

    def get_alignment(self) -> Alignment: ...

    def get_attributes(self) -> typing.Optional[AttrList]: ...

    def get_auto_dir(self) -> builtins.bool: ...

    def get_baseline(self) -> builtins.int: ...

    def get_character_count(self) -> builtins.int: ...

    def get_context(self) -> Context: ...

    def get_cursor_pos(self, index_: builtins.int) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_direction(self, index: builtins.int) -> Direction: ...

    def get_ellipsize(self) -> EllipsizeMode: ...

    def get_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_font_description(self) -> typing.Optional[FontDescription]: ...

    def get_height(self) -> builtins.int: ...

    def get_indent(self) -> builtins.int: ...

    def get_iter(self) -> LayoutIter: ...

    def get_justify(self) -> builtins.bool: ...

    def get_line(self, line: builtins.int) -> typing.Optional[LayoutLine]: ...

    def get_line_count(self) -> builtins.int: ...

    def get_line_readonly(self, line: builtins.int) -> typing.Optional[LayoutLine]: ...

    def get_line_spacing(self) -> builtins.float: ...

    def get_lines(self) -> typing.Sequence[LayoutLine]: ...

    def get_lines_readonly(self) -> typing.Sequence[LayoutLine]: ...

    def get_log_attrs(self) -> typing.Sequence[LogAttr]: ...

    def get_log_attrs_readonly(self) -> typing.Sequence[LogAttr]: ...

    def get_pixel_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_pixel_size(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_serial(self) -> builtins.int: ...

    def get_single_paragraph_mode(self) -> builtins.bool: ...

    def get_size(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_spacing(self) -> builtins.int: ...

    def get_tabs(self) -> typing.Optional[TabArray]: ...

    def get_text(self) -> builtins.str: ...

    def get_unknown_glyphs_count(self) -> builtins.int: ...

    def get_width(self) -> builtins.int: ...

    def get_wrap(self) -> WrapMode: ...

    def index_to_line_x(self, index_: builtins.int, trailing: builtins.bool) -> typing.Tuple[builtins.int, builtins.int]: ...

    def index_to_pos(self, index_: builtins.int) -> Rectangle: ...

    def is_ellipsized(self) -> builtins.bool: ...

    def is_wrapped(self) -> builtins.bool: ...

    def move_cursor_visually(self, strong: builtins.bool, old_index: builtins.int, old_trailing: builtins.int, direction: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...

    @staticmethod
    def new(context: Context, **kwargs) -> Layout: ...  # type: ignore

    def set_alignment(self, alignment: Alignment) -> None: ...

    def set_attributes(self, attrs: typing.Optional[AttrList]) -> None: ...

    def set_auto_dir(self, auto_dir: builtins.bool) -> None: ...

    def set_ellipsize(self, ellipsize: EllipsizeMode) -> None: ...

    def set_font_description(self, desc: typing.Optional[FontDescription]) -> None: ...

    def set_height(self, height: builtins.int) -> None: ...

    def set_indent(self, indent: builtins.int) -> None: ...

    def set_justify(self, justify: builtins.bool) -> None: ...

    def set_line_spacing(self, factor: builtins.float) -> None: ...

    def set_markup(self, markup: builtins.str, length: builtins.int) -> None: ...

    def set_markup_with_accel(self, markup: builtins.str, length: builtins.int, accel_marker: builtins.str) -> builtins.str: ...

    def set_single_paragraph_mode(self, setting: builtins.bool) -> None: ...

    def set_spacing(self, spacing: builtins.int) -> None: ...

    def set_tabs(self, tabs: typing.Optional[TabArray]) -> None: ...

    def set_text(self, text: builtins.str, length: builtins.int) -> None: ...

    def set_width(self, width: builtins.int) -> None: ...

    def set_wrap(self, wrap: WrapMode) -> None: ...

    def xy_to_index(self, x: builtins.int, y: builtins.int) -> typing.Tuple[builtins.bool, builtins.int, builtins.int]: ...


class Renderer(GObject.Object):
    active_count: builtins.int
    matrix: Matrix
    parent_instance: GObject.Object
    strikethrough: builtins.bool
    underline: Underline

    def activate(self) -> None: ...

    def deactivate(self) -> None: ...

    def draw_error_underline(self, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...

    def draw_glyph(self, font: Font, glyph: builtins.int, x: builtins.float, y: builtins.float) -> None: ...

    def draw_glyph_item(self, text: typing.Optional[builtins.str], glyph_item: GlyphItem, x: builtins.int, y: builtins.int) -> None: ...

    def draw_glyphs(self, font: Font, glyphs: GlyphString, x: builtins.int, y: builtins.int) -> None: ...

    def draw_layout(self, layout: Layout, x: builtins.int, y: builtins.int) -> None: ...

    def draw_layout_line(self, line: LayoutLine, x: builtins.int, y: builtins.int) -> None: ...

    def draw_rectangle(self, part: RenderPart, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...

    def draw_trapezoid(self, part: RenderPart, y1_: builtins.float, x11: builtins.float, x21: builtins.float, y2: builtins.float, x12: builtins.float, x22: builtins.float) -> None: ...

    def get_alpha(self, part: RenderPart) -> builtins.int: ...

    def get_color(self, part: RenderPart) -> typing.Optional[Color]: ...

    def get_layout(self) -> typing.Optional[Layout]: ...

    def get_layout_line(self) -> typing.Optional[LayoutLine]: ...

    def get_matrix(self) -> typing.Optional[Matrix]: ...

    def part_changed(self, part: RenderPart) -> None: ...

    def set_alpha(self, part: RenderPart, alpha: builtins.int) -> None: ...

    def set_color(self, part: RenderPart, color: typing.Optional[Color]) -> None: ...

    def set_matrix(self, matrix: typing.Optional[Matrix]) -> None: ...

    def do_begin(self) -> None: ...

    def do_draw_error_underline(self, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...

    def do_draw_glyph(self, font: Font, glyph: builtins.int, x: builtins.float, y: builtins.float) -> None: ...

    def do_draw_glyph_item(self, text: typing.Optional[builtins.str], glyph_item: GlyphItem, x: builtins.int, y: builtins.int) -> None: ...

    def do_draw_glyphs(self, font: Font, glyphs: GlyphString, x: builtins.int, y: builtins.int) -> None: ...

    def do_draw_rectangle(self, part: RenderPart, x: builtins.int, y: builtins.int, width: builtins.int, height: builtins.int) -> None: ...

    def do_draw_shape(self, attr: AttrShape, x: builtins.int, y: builtins.int) -> None: ...

    def do_draw_trapezoid(self, part: RenderPart, y1_: builtins.float, x11: builtins.float, x21: builtins.float, y2: builtins.float, x12: builtins.float, x22: builtins.float) -> None: ...

    def do_end(self) -> None: ...

    def do_part_changed(self, part: RenderPart) -> None: ...

    def do_prepare_run(self, run: GlyphItem) -> None: ...


class EngineLang(Engine):
    parent_instance: Engine

    def do_script_break(self, text: builtins.str, len: builtins.int, analysis: Analysis, attrs: LogAttr, attrs_len: builtins.int) -> None: ...


class EngineShape(Engine):
    parent_instance: Engine

    def do_covers(self, font: Font, language: Language, wc: builtins.str) -> CoverageLevel: ...

    def do_script_shape(self, font: Font, item_text: builtins.str, item_length: builtins.int, analysis: Analysis, glyphs: GlyphString, paragraph_text: builtins.str, paragraph_length: builtins.int) -> None: ...


class FontsetSimple(Fontset):

    def append(self, font: Font) -> None: ...

    @staticmethod
    def new(language: Language) -> FontsetSimple: ...

    def size(self) -> builtins.int: ...


class Analysis():
    extra_attrs: typing.Sequence[builtins.object]
    flags: builtins.int
    font: Font
    gravity: builtins.int
    lang_engine: EngineLang
    language: Language
    level: builtins.int
    script: builtins.int
    shape_engine: EngineShape


class AttrClass():
    copy: builtins.object
    destroy: builtins.object
    equal: builtins.object
    type: AttrType


class AttrColor():
    attr: Attribute
    color: Color


class AttrFloat():
    attr: Attribute
    value: builtins.float


class AttrFontDesc():
    attr: Attribute
    desc: FontDescription

    @staticmethod
    def new(desc: FontDescription) -> Attribute: ...


class AttrFontFeatures():
    attr: Attribute
    features: builtins.str

    @staticmethod
    def new(features: builtins.str) -> Attribute: ...


class AttrInt():
    attr: Attribute
    value: builtins.int


class AttrIterator():

    def copy(self) -> AttrIterator: ...

    def destroy(self) -> None: ...

    def get(self, type: AttrType) -> typing.Optional[Attribute]: ...

    def get_attrs(self) -> typing.Sequence[Attribute]: ...

    def get_font(self, desc: FontDescription, language: typing.Optional[Language], extra_attrs: typing.Optional[typing.Sequence[Attribute]]) -> None: ...

    def next(self) -> builtins.bool: ...

    def range(self) -> typing.Tuple[builtins.int, builtins.int]: ...


class AttrLanguage():
    attr: Attribute
    value: Language

    @staticmethod
    def new(language: Language) -> Attribute: ...


class AttrList():

    def change(self, attr: Attribute) -> None: ...

    def copy(self) -> typing.Optional[AttrList]: ...

    def equal(self, other_list: AttrList) -> builtins.bool: ...

    def filter(self, func: AttrFilterFunc, *data: typing.Optional[builtins.object]) -> typing.Optional[AttrList]: ...

    def get_attributes(self) -> typing.Sequence[Attribute]: ...

    def get_iterator(self) -> AttrIterator: ...

    def insert(self, attr: Attribute) -> None: ...

    def insert_before(self, attr: Attribute) -> None: ...

    @staticmethod
    def new() -> AttrList: ...

    def ref(self) -> AttrList: ...

    def splice(self, other: AttrList, pos: builtins.int, len: builtins.int) -> None: ...

    def unref(self) -> None: ...

    def update(self, pos: builtins.int, remove: builtins.int, add: builtins.int) -> None: ...


class AttrShape():
    attr: Attribute
    copy_func: AttrDataCopyFunc
    data: builtins.object
    destroy_func: GLib.DestroyNotify
    ink_rect: Rectangle
    logical_rect: Rectangle

    @staticmethod
    def new(ink_rect: Rectangle, logical_rect: Rectangle) -> Attribute: ...

    @staticmethod
    def new_with_data(ink_rect: Rectangle, logical_rect: Rectangle, data: typing.Optional[builtins.object], copy_func: typing.Optional[AttrDataCopyFunc]) -> Attribute: ...


class AttrSize():
    absolute: builtins.int
    attr: Attribute
    size: builtins.int

    @staticmethod
    def new(size: builtins.int) -> Attribute: ...

    @staticmethod
    def new_absolute(size: builtins.int) -> Attribute: ...


class AttrString():
    attr: Attribute
    value: builtins.str


class Attribute():
    end_index: builtins.int
    klass: AttrClass
    start_index: builtins.int

    def copy(self) -> Attribute: ...

    def destroy(self) -> None: ...

    def equal(self, attr2: Attribute) -> builtins.bool: ...

    def init(self, klass: AttrClass) -> None: ...


class Color():
    blue: builtins.int
    green: builtins.int
    red: builtins.int

    def copy(self) -> typing.Optional[Color]: ...

    def free(self) -> None: ...

    def parse(self, spec: builtins.str) -> builtins.bool: ...

    def parse_with_alpha(self, spec: builtins.str) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def to_string(self) -> builtins.str: ...


class EngineInfo():
    engine_type: builtins.str
    id: builtins.str
    n_scripts: builtins.int
    render_type: builtins.str
    scripts: EngineScriptInfo


class EngineScriptInfo():
    langs: builtins.str
    script: Script


class FontDescription():

    def better_match(self, old_match: typing.Optional[FontDescription], new_match: FontDescription) -> builtins.bool: ...

    def copy(self) -> typing.Optional[FontDescription]: ...

    def copy_static(self) -> typing.Optional[FontDescription]: ...

    def equal(self, desc2: FontDescription) -> builtins.bool: ...

    def free(self) -> None: ...

    @staticmethod
    def from_string(str: builtins.str) -> FontDescription: ...

    def get_family(self) -> typing.Optional[builtins.str]: ...

    def get_gravity(self) -> Gravity: ...

    def get_set_fields(self) -> FontMask: ...

    def get_size(self) -> builtins.int: ...

    def get_size_is_absolute(self) -> builtins.bool: ...

    def get_stretch(self) -> Stretch: ...

    def get_style(self) -> Style: ...

    def get_variant(self) -> Variant: ...

    def get_variations(self) -> typing.Optional[builtins.str]: ...

    def get_weight(self) -> Weight: ...

    def hash(self) -> builtins.int: ...

    def merge(self, desc_to_merge: typing.Optional[FontDescription], replace_existing: builtins.bool) -> None: ...

    def merge_static(self, desc_to_merge: FontDescription, replace_existing: builtins.bool) -> None: ...

    @staticmethod
    def new() -> FontDescription: ...

    def set_absolute_size(self, size: builtins.float) -> None: ...

    def set_family(self, family: builtins.str) -> None: ...

    def set_family_static(self, family: builtins.str) -> None: ...

    def set_gravity(self, gravity: Gravity) -> None: ...

    def set_size(self, size: builtins.int) -> None: ...

    def set_stretch(self, stretch: Stretch) -> None: ...

    def set_style(self, style: Style) -> None: ...

    def set_variant(self, variant: Variant) -> None: ...

    def set_variations(self, variations: builtins.str) -> None: ...

    def set_variations_static(self, variations: builtins.str) -> None: ...

    def set_weight(self, weight: Weight) -> None: ...

    def to_filename(self) -> builtins.str: ...

    def to_string(self) -> builtins.str: ...

    def unset_fields(self, to_unset: FontMask) -> None: ...


class FontMetrics():
    approximate_char_width: builtins.int
    approximate_digit_width: builtins.int
    ascent: builtins.int
    descent: builtins.int
    height: builtins.int
    ref_count: builtins.int
    strikethrough_position: builtins.int
    strikethrough_thickness: builtins.int
    underline_position: builtins.int
    underline_thickness: builtins.int

    def get_approximate_char_width(self) -> builtins.int: ...

    def get_approximate_digit_width(self) -> builtins.int: ...

    def get_ascent(self) -> builtins.int: ...

    def get_descent(self) -> builtins.int: ...

    def get_height(self) -> builtins.int: ...

    def get_strikethrough_position(self) -> builtins.int: ...

    def get_strikethrough_thickness(self) -> builtins.int: ...

    def get_underline_position(self) -> builtins.int: ...

    def get_underline_thickness(self) -> builtins.int: ...

    def ref(self) -> typing.Optional[FontMetrics]: ...

    def unref(self) -> None: ...


class GlyphGeometry():
    width: builtins.int
    x_offset: builtins.int
    y_offset: builtins.int


class GlyphInfo():
    attr: GlyphVisAttr
    geometry: GlyphGeometry
    glyph: builtins.int


class GlyphItem():
    glyphs: GlyphString
    item: Item

    def apply_attrs(self, text: builtins.str, list: AttrList) -> typing.Sequence[GlyphItem]: ...

    def copy(self) -> typing.Optional[GlyphItem]: ...

    def free(self) -> None: ...

    def get_logical_widths(self, text: builtins.str, logical_widths: typing.Sequence[builtins.int]) -> None: ...

    def letter_space(self, text: builtins.str, log_attrs: typing.Sequence[LogAttr], letter_spacing: builtins.int) -> None: ...

    def split(self, text: builtins.str, split_index: builtins.int) -> GlyphItem: ...


class GlyphItemIter():
    end_char: builtins.int
    end_glyph: builtins.int
    end_index: builtins.int
    glyph_item: GlyphItem
    start_char: builtins.int
    start_glyph: builtins.int
    start_index: builtins.int
    text: builtins.str

    def copy(self) -> typing.Optional[GlyphItemIter]: ...

    def free(self) -> None: ...

    def init_end(self, glyph_item: GlyphItem, text: builtins.str) -> builtins.bool: ...

    def init_start(self, glyph_item: GlyphItem, text: builtins.str) -> builtins.bool: ...

    def next_cluster(self) -> builtins.bool: ...

    def prev_cluster(self) -> builtins.bool: ...


class GlyphString():
    glyphs: typing.Sequence[GlyphInfo]
    log_clusters: builtins.int
    num_glyphs: builtins.int
    space: builtins.int

    def copy(self) -> typing.Optional[GlyphString]: ...

    def extents(self, font: Font) -> typing.Tuple[Rectangle, Rectangle]: ...

    def extents_range(self, start: builtins.int, end: builtins.int, font: Font) -> typing.Tuple[Rectangle, Rectangle]: ...

    def free(self) -> None: ...

    def get_logical_widths(self, text: builtins.str, length: builtins.int, embedding_level: builtins.int, logical_widths: typing.Sequence[builtins.int]) -> None: ...

    def get_width(self) -> builtins.int: ...

    def index_to_x(self, text: builtins.str, length: builtins.int, analysis: Analysis, index_: builtins.int, trailing: builtins.bool) -> builtins.int: ...

    @staticmethod
    def new() -> GlyphString: ...

    def set_size(self, new_len: builtins.int) -> None: ...

    def x_to_index(self, text: builtins.str, length: builtins.int, analysis: Analysis, x_pos: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


class GlyphVisAttr():
    is_cluster_start: builtins.int


class IncludedModule():
    create: builtins.object
    exit: builtins.object
    init: builtins.object
    list: builtins.object


class Item():
    analysis: Analysis
    length: builtins.int
    num_chars: builtins.int
    offset: builtins.int

    def apply_attrs(self, iter: AttrIterator) -> None: ...

    def copy(self) -> typing.Optional[Item]: ...

    def free(self) -> None: ...

    @staticmethod
    def new() -> Item: ...

    def split(self, split_index: builtins.int, split_offset: builtins.int) -> Item: ...


class Language():

    @staticmethod
    def from_string(language: typing.Optional[builtins.str]) -> typing.Optional[Language]: ...

    @staticmethod
    def get_default() -> Language: ...

    def get_sample_string(self) -> builtins.str: ...

    def get_scripts(self) -> typing.Optional[typing.Sequence[Script]]: ...

    def includes_script(self, script: Script) -> builtins.bool: ...

    def matches(self, range_list: builtins.str) -> builtins.bool: ...

    def to_string(self) -> builtins.str: ...


class LayoutIter():

    def at_last_line(self) -> builtins.bool: ...

    def copy(self) -> typing.Optional[LayoutIter]: ...

    def free(self) -> None: ...

    def get_baseline(self) -> builtins.int: ...

    def get_char_extents(self) -> Rectangle: ...

    def get_cluster_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_index(self) -> builtins.int: ...

    def get_layout(self) -> Layout: ...

    def get_layout_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_line(self) -> LayoutLine: ...

    def get_line_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_line_readonly(self) -> LayoutLine: ...

    def get_line_yrange(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_run(self) -> typing.Optional[GlyphItem]: ...

    def get_run_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_run_readonly(self) -> typing.Optional[GlyphItem]: ...

    def next_char(self) -> builtins.bool: ...

    def next_cluster(self) -> builtins.bool: ...

    def next_line(self) -> builtins.bool: ...

    def next_run(self) -> builtins.bool: ...


class LayoutLine():
    is_paragraph_start: builtins.int
    layout: Layout
    length: builtins.int
    resolved_dir: builtins.int
    runs: typing.Sequence[GlyphItem]
    start_index: builtins.int

    def get_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_height(self) -> builtins.int: ...

    def get_pixel_extents(self) -> typing.Tuple[Rectangle, Rectangle]: ...

    def get_x_ranges(self, start_index: builtins.int, end_index: builtins.int) -> typing.Sequence[builtins.int]: ...

    def index_to_x(self, index_: builtins.int, trailing: builtins.bool) -> builtins.int: ...

    def ref(self) -> LayoutLine: ...

    def unref(self) -> None: ...

    def x_to_index(self, x_pos: builtins.int) -> typing.Tuple[builtins.bool, builtins.int, builtins.int]: ...


class LogAttr():
    backspace_deletes_character: builtins.int
    is_char_break: builtins.int
    is_cursor_position: builtins.int
    is_expandable_space: builtins.int
    is_line_break: builtins.int
    is_mandatory_break: builtins.int
    is_sentence_boundary: builtins.int
    is_sentence_end: builtins.int
    is_sentence_start: builtins.int
    is_white: builtins.int
    is_word_boundary: builtins.int
    is_word_end: builtins.int
    is_word_start: builtins.int


class Map():
    ...


class MapEntry():
    ...


class Matrix():
    x0: builtins.float
    xx: builtins.float
    xy: builtins.float
    y0: builtins.float
    yx: builtins.float
    yy: builtins.float

    def concat(self, new_matrix: Matrix) -> None: ...

    def copy(self) -> typing.Optional[Matrix]: ...

    def free(self) -> None: ...

    def get_font_scale_factor(self) -> builtins.float: ...

    def get_font_scale_factors(self) -> typing.Tuple[builtins.float, builtins.float]: ...

    def rotate(self, degrees: builtins.float) -> None: ...

    def scale(self, scale_x: builtins.float, scale_y: builtins.float) -> None: ...

    def transform_distance(self, dx: builtins.float, dy: builtins.float) -> typing.Tuple[builtins.float, builtins.float]: ...

    def transform_pixel_rectangle(self, rect: typing.Optional[Rectangle]) -> typing.Optional[Rectangle]: ...

    def transform_point(self, x: builtins.float, y: builtins.float) -> typing.Tuple[builtins.float, builtins.float]: ...

    def transform_rectangle(self, rect: typing.Optional[Rectangle]) -> typing.Optional[Rectangle]: ...

    def translate(self, tx: builtins.float, ty: builtins.float) -> None: ...


class Rectangle():
    height: builtins.int
    width: builtins.int
    x: builtins.int
    y: builtins.int


class ScriptIter():

    def free(self) -> None: ...

    def get_range(self) -> typing.Tuple[builtins.str, builtins.str, Script]: ...

    @staticmethod
    def new(text: builtins.str, length: builtins.int) -> ScriptIter: ...

    def next(self) -> builtins.bool: ...


class TabArray():

    def copy(self) -> TabArray: ...

    def free(self) -> None: ...

    def get_positions_in_pixels(self) -> builtins.bool: ...

    def get_size(self) -> builtins.int: ...

    def get_tab(self, tab_index: builtins.int) -> typing.Tuple[TabAlign, builtins.int]: ...

    def get_tabs(self) -> typing.Tuple[TabAlign, typing.Sequence[builtins.int]]: ...

    @staticmethod
    def new(initial_size: builtins.int, positions_in_pixels: builtins.bool) -> TabArray: ...

    def resize(self, new_size: builtins.int) -> None: ...

    def set_tab(self, tab_index: builtins.int, alignment: TabAlign, location: builtins.int) -> None: ...


class FontMask(GObject.GFlags, builtins.int):
    FAMILY = ...  # type: FontMask
    GRAVITY = ...  # type: FontMask
    SIZE = ...  # type: FontMask
    STRETCH = ...  # type: FontMask
    STYLE = ...  # type: FontMask
    VARIANT = ...  # type: FontMask
    VARIATIONS = ...  # type: FontMask
    WEIGHT = ...  # type: FontMask


class ShapeFlags(GObject.GFlags, builtins.int):
    NONE = ...  # type: ShapeFlags
    ROUND_POSITIONS = ...  # type: ShapeFlags


class ShowFlags(GObject.GFlags, builtins.int):
    IGNORABLES = ...  # type: ShowFlags
    LINE_BREAKS = ...  # type: ShowFlags
    NONE = ...  # type: ShowFlags
    SPACES = ...  # type: ShowFlags


class Alignment(GObject.GEnum, builtins.int):
    CENTER = ...  # type: Alignment
    LEFT = ...  # type: Alignment
    RIGHT = ...  # type: Alignment


class AttrType(GObject.GEnum, builtins.int):
    ABSOLUTE_SIZE = ...  # type: AttrType
    ALLOW_BREAKS = ...  # type: AttrType
    BACKGROUND = ...  # type: AttrType
    BACKGROUND_ALPHA = ...  # type: AttrType
    FALLBACK = ...  # type: AttrType
    FAMILY = ...  # type: AttrType
    FONT_DESC = ...  # type: AttrType
    FONT_FEATURES = ...  # type: AttrType
    FOREGROUND = ...  # type: AttrType
    FOREGROUND_ALPHA = ...  # type: AttrType
    GRAVITY = ...  # type: AttrType
    GRAVITY_HINT = ...  # type: AttrType
    INSERT_HYPHENS = ...  # type: AttrType
    INVALID = ...  # type: AttrType
    LANGUAGE = ...  # type: AttrType
    LETTER_SPACING = ...  # type: AttrType
    OVERLINE = ...  # type: AttrType
    OVERLINE_COLOR = ...  # type: AttrType
    RISE = ...  # type: AttrType
    SCALE = ...  # type: AttrType
    SHAPE = ...  # type: AttrType
    SHOW = ...  # type: AttrType
    SIZE = ...  # type: AttrType
    STRETCH = ...  # type: AttrType
    STRIKETHROUGH = ...  # type: AttrType
    STRIKETHROUGH_COLOR = ...  # type: AttrType
    STYLE = ...  # type: AttrType
    UNDERLINE = ...  # type: AttrType
    UNDERLINE_COLOR = ...  # type: AttrType
    VARIANT = ...  # type: AttrType
    WEIGHT = ...  # type: AttrType

    @staticmethod
    def get_name(type: AttrType) -> typing.Optional[builtins.str]: ...

    @staticmethod
    def register(name: builtins.str) -> AttrType: ...


class BidiType(GObject.GEnum, builtins.int):
    AL = ...  # type: BidiType
    AN = ...  # type: BidiType
    B = ...  # type: BidiType
    BN = ...  # type: BidiType
    CS = ...  # type: BidiType
    EN = ...  # type: BidiType
    ES = ...  # type: BidiType
    ET = ...  # type: BidiType
    L = ...  # type: BidiType
    LRE = ...  # type: BidiType
    LRO = ...  # type: BidiType
    NSM = ...  # type: BidiType
    ON = ...  # type: BidiType
    PDF = ...  # type: BidiType
    R = ...  # type: BidiType
    RLE = ...  # type: BidiType
    RLO = ...  # type: BidiType
    S = ...  # type: BidiType
    WS = ...  # type: BidiType

    @staticmethod
    def for_unichar(ch: builtins.str) -> BidiType: ...


class CoverageLevel(GObject.GEnum, builtins.int):
    APPROXIMATE = ...  # type: CoverageLevel
    EXACT = ...  # type: CoverageLevel
    FALLBACK = ...  # type: CoverageLevel
    NONE = ...  # type: CoverageLevel


class Direction(GObject.GEnum, builtins.int):
    LTR = ...  # type: Direction
    NEUTRAL = ...  # type: Direction
    RTL = ...  # type: Direction
    TTB_LTR = ...  # type: Direction
    TTB_RTL = ...  # type: Direction
    WEAK_LTR = ...  # type: Direction
    WEAK_RTL = ...  # type: Direction


class EllipsizeMode(GObject.GEnum, builtins.int):
    END = ...  # type: EllipsizeMode
    MIDDLE = ...  # type: EllipsizeMode
    NONE = ...  # type: EllipsizeMode
    START = ...  # type: EllipsizeMode


class Gravity(GObject.GEnum, builtins.int):
    AUTO = ...  # type: Gravity
    EAST = ...  # type: Gravity
    NORTH = ...  # type: Gravity
    SOUTH = ...  # type: Gravity
    WEST = ...  # type: Gravity

    @staticmethod
    def get_for_matrix(matrix: typing.Optional[Matrix]) -> Gravity: ...

    @staticmethod
    def get_for_script(script: Script, base_gravity: Gravity, hint: GravityHint) -> Gravity: ...

    @staticmethod
    def get_for_script_and_width(script: Script, wide: builtins.bool, base_gravity: Gravity, hint: GravityHint) -> Gravity: ...

    @staticmethod
    def to_rotation(gravity: Gravity) -> builtins.float: ...


class GravityHint(GObject.GEnum, builtins.int):
    LINE = ...  # type: GravityHint
    NATURAL = ...  # type: GravityHint
    STRONG = ...  # type: GravityHint


class Overline(GObject.GEnum, builtins.int):
    NONE = ...  # type: Overline
    SINGLE = ...  # type: Overline


class RenderPart(GObject.GEnum, builtins.int):
    BACKGROUND = ...  # type: RenderPart
    FOREGROUND = ...  # type: RenderPart
    OVERLINE = ...  # type: RenderPart
    STRIKETHROUGH = ...  # type: RenderPart
    UNDERLINE = ...  # type: RenderPart


class Script(GObject.GEnum, builtins.int):
    AHOM = ...  # type: Script
    ANATOLIAN_HIEROGLYPHS = ...  # type: Script
    ARABIC = ...  # type: Script
    ARMENIAN = ...  # type: Script
    BALINESE = ...  # type: Script
    BASSA_VAH = ...  # type: Script
    BATAK = ...  # type: Script
    BENGALI = ...  # type: Script
    BOPOMOFO = ...  # type: Script
    BRAHMI = ...  # type: Script
    BRAILLE = ...  # type: Script
    BUGINESE = ...  # type: Script
    BUHID = ...  # type: Script
    CANADIAN_ABORIGINAL = ...  # type: Script
    CARIAN = ...  # type: Script
    CAUCASIAN_ALBANIAN = ...  # type: Script
    CHAKMA = ...  # type: Script
    CHAM = ...  # type: Script
    CHEROKEE = ...  # type: Script
    COMMON = ...  # type: Script
    COPTIC = ...  # type: Script
    CUNEIFORM = ...  # type: Script
    CYPRIOT = ...  # type: Script
    CYRILLIC = ...  # type: Script
    DESERET = ...  # type: Script
    DEVANAGARI = ...  # type: Script
    DUPLOYAN = ...  # type: Script
    ELBASAN = ...  # type: Script
    ETHIOPIC = ...  # type: Script
    GEORGIAN = ...  # type: Script
    GLAGOLITIC = ...  # type: Script
    GOTHIC = ...  # type: Script
    GRANTHA = ...  # type: Script
    GREEK = ...  # type: Script
    GUJARATI = ...  # type: Script
    GURMUKHI = ...  # type: Script
    HAN = ...  # type: Script
    HANGUL = ...  # type: Script
    HANUNOO = ...  # type: Script
    HATRAN = ...  # type: Script
    HEBREW = ...  # type: Script
    HIRAGANA = ...  # type: Script
    INHERITED = ...  # type: Script
    INVALID_CODE = ...  # type: Script
    KANNADA = ...  # type: Script
    KATAKANA = ...  # type: Script
    KAYAH_LI = ...  # type: Script
    KHAROSHTHI = ...  # type: Script
    KHMER = ...  # type: Script
    KHOJKI = ...  # type: Script
    KHUDAWADI = ...  # type: Script
    LAO = ...  # type: Script
    LATIN = ...  # type: Script
    LEPCHA = ...  # type: Script
    LIMBU = ...  # type: Script
    LINEAR_A = ...  # type: Script
    LINEAR_B = ...  # type: Script
    LYCIAN = ...  # type: Script
    LYDIAN = ...  # type: Script
    MAHAJANI = ...  # type: Script
    MALAYALAM = ...  # type: Script
    MANDAIC = ...  # type: Script
    MANICHAEAN = ...  # type: Script
    MENDE_KIKAKUI = ...  # type: Script
    MEROITIC_CURSIVE = ...  # type: Script
    MEROITIC_HIEROGLYPHS = ...  # type: Script
    MIAO = ...  # type: Script
    MODI = ...  # type: Script
    MONGOLIAN = ...  # type: Script
    MRO = ...  # type: Script
    MULTANI = ...  # type: Script
    MYANMAR = ...  # type: Script
    NABATAEAN = ...  # type: Script
    NEW_TAI_LUE = ...  # type: Script
    NKO = ...  # type: Script
    OGHAM = ...  # type: Script
    OLD_HUNGARIAN = ...  # type: Script
    OLD_ITALIC = ...  # type: Script
    OLD_NORTH_ARABIAN = ...  # type: Script
    OLD_PERMIC = ...  # type: Script
    OLD_PERSIAN = ...  # type: Script
    OL_CHIKI = ...  # type: Script
    ORIYA = ...  # type: Script
    OSMANYA = ...  # type: Script
    PAHAWH_HMONG = ...  # type: Script
    PALMYRENE = ...  # type: Script
    PAU_CIN_HAU = ...  # type: Script
    PHAGS_PA = ...  # type: Script
    PHOENICIAN = ...  # type: Script
    PSALTER_PAHLAVI = ...  # type: Script
    REJANG = ...  # type: Script
    RUNIC = ...  # type: Script
    SAURASHTRA = ...  # type: Script
    SHARADA = ...  # type: Script
    SHAVIAN = ...  # type: Script
    SIDDHAM = ...  # type: Script
    SIGNWRITING = ...  # type: Script
    SINHALA = ...  # type: Script
    SORA_SOMPENG = ...  # type: Script
    SUNDANESE = ...  # type: Script
    SYLOTI_NAGRI = ...  # type: Script
    SYRIAC = ...  # type: Script
    TAGALOG = ...  # type: Script
    TAGBANWA = ...  # type: Script
    TAI_LE = ...  # type: Script
    TAKRI = ...  # type: Script
    TAMIL = ...  # type: Script
    TELUGU = ...  # type: Script
    THAANA = ...  # type: Script
    THAI = ...  # type: Script
    TIBETAN = ...  # type: Script
    TIFINAGH = ...  # type: Script
    TIRHUTA = ...  # type: Script
    UGARITIC = ...  # type: Script
    UNKNOWN = ...  # type: Script
    VAI = ...  # type: Script
    WARANG_CITI = ...  # type: Script
    YI = ...  # type: Script

    @staticmethod
    def for_unichar(ch: builtins.str) -> Script: ...

    @staticmethod
    def get_sample_language(script: Script) -> typing.Optional[Language]: ...


class Stretch(GObject.GEnum, builtins.int):
    CONDENSED = ...  # type: Stretch
    EXPANDED = ...  # type: Stretch
    EXTRA_CONDENSED = ...  # type: Stretch
    EXTRA_EXPANDED = ...  # type: Stretch
    NORMAL = ...  # type: Stretch
    SEMI_CONDENSED = ...  # type: Stretch
    SEMI_EXPANDED = ...  # type: Stretch
    ULTRA_CONDENSED = ...  # type: Stretch
    ULTRA_EXPANDED = ...  # type: Stretch


class Style(GObject.GEnum, builtins.int):
    ITALIC = ...  # type: Style
    NORMAL = ...  # type: Style
    OBLIQUE = ...  # type: Style


class TabAlign(GObject.GEnum, builtins.int):
    LEFT = ...  # type: TabAlign


class Underline(GObject.GEnum, builtins.int):
    DOUBLE = ...  # type: Underline
    DOUBLE_LINE = ...  # type: Underline
    ERROR = ...  # type: Underline
    ERROR_LINE = ...  # type: Underline
    LOW = ...  # type: Underline
    NONE = ...  # type: Underline
    SINGLE = ...  # type: Underline
    SINGLE_LINE = ...  # type: Underline


class Variant(GObject.GEnum, builtins.int):
    NORMAL = ...  # type: Variant
    SMALL_CAPS = ...  # type: Variant


class Weight(GObject.GEnum, builtins.int):
    BOLD = ...  # type: Weight
    BOOK = ...  # type: Weight
    HEAVY = ...  # type: Weight
    LIGHT = ...  # type: Weight
    MEDIUM = ...  # type: Weight
    NORMAL = ...  # type: Weight
    SEMIBOLD = ...  # type: Weight
    SEMILIGHT = ...  # type: Weight
    THIN = ...  # type: Weight
    ULTRABOLD = ...  # type: Weight
    ULTRAHEAVY = ...  # type: Weight
    ULTRALIGHT = ...  # type: Weight


class WrapMode(GObject.GEnum, builtins.int):
    CHAR = ...  # type: WrapMode
    WORD = ...  # type: WrapMode
    WORD_CHAR = ...  # type: WrapMode


AttrDataCopyFunc = typing.Callable[[typing.Optional[builtins.object]], typing.Optional[builtins.object]]
AttrFilterFunc = typing.Callable[[Attribute, typing.Optional[builtins.object]], builtins.bool]
FontsetForeachFunc = typing.Callable[[Fontset, Font, typing.Optional[builtins.object]], builtins.bool]


def attr_allow_breaks_new(allow_breaks: builtins.bool) -> Attribute: ...


def attr_background_alpha_new(alpha: builtins.int) -> Attribute: ...


def attr_background_new(red: builtins.int, green: builtins.int, blue: builtins.int) -> Attribute: ...


def attr_fallback_new(enable_fallback: builtins.bool) -> Attribute: ...


def attr_family_new(family: builtins.str) -> Attribute: ...


def attr_font_desc_new(desc: FontDescription) -> Attribute: ...


def attr_font_features_new(features: builtins.str) -> Attribute: ...


def attr_foreground_alpha_new(alpha: builtins.int) -> Attribute: ...


def attr_foreground_new(red: builtins.int, green: builtins.int, blue: builtins.int) -> Attribute: ...


def attr_gravity_hint_new(hint: GravityHint) -> Attribute: ...


def attr_gravity_new(gravity: Gravity) -> Attribute: ...


def attr_insert_hyphens_new(insert_hyphens: builtins.bool) -> Attribute: ...


def attr_language_new(language: Language) -> Attribute: ...


def attr_letter_spacing_new(letter_spacing: builtins.int) -> Attribute: ...


def attr_overline_color_new(red: builtins.int, green: builtins.int, blue: builtins.int) -> Attribute: ...


def attr_overline_new(overline: Overline) -> Attribute: ...


def attr_rise_new(rise: builtins.int) -> Attribute: ...


def attr_scale_new(scale_factor: builtins.float) -> Attribute: ...


def attr_shape_new(ink_rect: Rectangle, logical_rect: Rectangle) -> Attribute: ...


def attr_shape_new_with_data(ink_rect: Rectangle, logical_rect: Rectangle, data: typing.Optional[builtins.object], copy_func: typing.Optional[AttrDataCopyFunc]) -> Attribute: ...


def attr_show_new(flags: ShowFlags) -> Attribute: ...


def attr_size_new(size: builtins.int) -> Attribute: ...


def attr_size_new_absolute(size: builtins.int) -> Attribute: ...


def attr_stretch_new(stretch: Stretch) -> Attribute: ...


def attr_strikethrough_color_new(red: builtins.int, green: builtins.int, blue: builtins.int) -> Attribute: ...


def attr_strikethrough_new(strikethrough: builtins.bool) -> Attribute: ...


def attr_style_new(style: Style) -> Attribute: ...


def attr_type_get_name(type: AttrType) -> typing.Optional[builtins.str]: ...


def attr_type_register(name: builtins.str) -> AttrType: ...


def attr_underline_color_new(red: builtins.int, green: builtins.int, blue: builtins.int) -> Attribute: ...


def attr_underline_new(underline: Underline) -> Attribute: ...


def attr_variant_new(variant: Variant) -> Attribute: ...


def attr_weight_new(weight: Weight) -> Attribute: ...


def bidi_type_for_unichar(ch: builtins.str) -> BidiType: ...


def break_(text: builtins.str, length: builtins.int, analysis: Analysis, attrs: typing.Sequence[LogAttr]) -> None: ...


def default_break(text: builtins.str, length: builtins.int, analysis: typing.Optional[Analysis], attrs: LogAttr, attrs_len: builtins.int) -> None: ...


def extents_to_pixels(inclusive: typing.Optional[Rectangle], nearest: typing.Optional[Rectangle]) -> None: ...


def find_base_dir(text: builtins.str, length: builtins.int) -> Direction: ...


def find_paragraph_boundary(text: builtins.str, length: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_description_from_string(str: builtins.str) -> FontDescription: ...


def get_log_attrs(text: builtins.str, length: builtins.int, level: builtins.int, language: Language, log_attrs: typing.Sequence[LogAttr]) -> None: ...


def get_mirror_char(ch: builtins.str, mirrored_ch: builtins.str) -> builtins.bool: ...


def gravity_get_for_matrix(matrix: typing.Optional[Matrix]) -> Gravity: ...


def gravity_get_for_script(script: Script, base_gravity: Gravity, hint: GravityHint) -> Gravity: ...


def gravity_get_for_script_and_width(script: Script, wide: builtins.bool, base_gravity: Gravity, hint: GravityHint) -> Gravity: ...


def gravity_to_rotation(gravity: Gravity) -> builtins.float: ...


def is_zero_width(ch: builtins.str) -> builtins.bool: ...


def itemize(context: Context, text: builtins.str, start_index: builtins.int, length: builtins.int, attrs: AttrList, cached_iter: typing.Optional[AttrIterator]) -> typing.Sequence[Item]: ...


def itemize_with_base_dir(context: Context, base_dir: Direction, text: builtins.str, start_index: builtins.int, length: builtins.int, attrs: AttrList, cached_iter: typing.Optional[AttrIterator]) -> typing.Sequence[Item]: ...


def language_from_string(language: typing.Optional[builtins.str]) -> typing.Optional[Language]: ...


def language_get_default() -> Language: ...


def log2vis_get_embedding_levels(text: builtins.str, length: builtins.int, pbase_dir: Direction) -> builtins.int: ...


def markup_parser_finish(context: GLib.MarkupParseContext) -> typing.Tuple[builtins.bool, AttrList, builtins.str, builtins.str]: ...


def markup_parser_new(accel_marker: builtins.str) -> GLib.MarkupParseContext: ...


def parse_enum(type: GObject.GType, str: typing.Optional[builtins.str], warn: builtins.bool) -> typing.Tuple[builtins.bool, builtins.int, builtins.str]: ...


def parse_markup(markup_text: builtins.str, length: builtins.int, accel_marker: builtins.str) -> typing.Tuple[builtins.bool, AttrList, builtins.str, builtins.str]: ...


def parse_stretch(str: builtins.str, warn: builtins.bool) -> typing.Tuple[builtins.bool, Stretch]: ...


def parse_style(str: builtins.str, warn: builtins.bool) -> typing.Tuple[builtins.bool, Style]: ...


def parse_variant(str: builtins.str, warn: builtins.bool) -> typing.Tuple[builtins.bool, Variant]: ...


def parse_weight(str: builtins.str, warn: builtins.bool) -> typing.Tuple[builtins.bool, Weight]: ...


def quantize_line_geometry(thickness: builtins.int, position: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def read_line(stream: typing.Optional[builtins.object], str: GLib.String) -> builtins.int: ...


def reorder_items(logical_items: typing.Sequence[Item]) -> typing.Sequence[Item]: ...


def scan_int(pos: builtins.str) -> typing.Tuple[builtins.bool, builtins.str, builtins.int]: ...


def scan_string(pos: builtins.str, out: GLib.String) -> typing.Tuple[builtins.bool, builtins.str]: ...


def scan_word(pos: builtins.str, out: GLib.String) -> typing.Tuple[builtins.bool, builtins.str]: ...


def script_for_unichar(ch: builtins.str) -> Script: ...


def script_get_sample_language(script: Script) -> typing.Optional[Language]: ...


def shape(text: builtins.str, length: builtins.int, analysis: Analysis, glyphs: GlyphString) -> None: ...


def shape_full(item_text: builtins.str, item_length: builtins.int, paragraph_text: typing.Optional[builtins.str], paragraph_length: builtins.int, analysis: Analysis, glyphs: GlyphString) -> None: ...


def shape_with_flags(item_text: builtins.str, item_length: builtins.int, paragraph_text: typing.Optional[builtins.str], paragraph_length: builtins.int, analysis: Analysis, glyphs: GlyphString, flags: ShapeFlags) -> None: ...


def skip_space(pos: builtins.str) -> typing.Tuple[builtins.bool, builtins.str]: ...


def split_file_list(str: builtins.str) -> typing.Sequence[builtins.str]: ...


def tailor_break(text: builtins.str, length: builtins.int, analysis: Analysis, offset: builtins.int, log_attrs: typing.Sequence[LogAttr]) -> None: ...


def trim_string(str: builtins.str) -> builtins.str: ...


def unichar_direction(ch: builtins.str) -> Direction: ...


def units_from_double(d: builtins.float) -> builtins.int: ...


def units_to_double(i: builtins.int) -> builtins.float: ...


def version() -> builtins.int: ...


def version_check(required_major: builtins.int, required_minor: builtins.int, required_micro: builtins.int) -> typing.Optional[builtins.str]: ...


def version_string() -> builtins.str: ...


ANALYSIS_FLAG_CENTERED_BASELINE: builtins.int
ANALYSIS_FLAG_IS_ELLIPSIS: builtins.int
ANALYSIS_FLAG_NEED_HYPHEN: builtins.int
ATTR_INDEX_FROM_TEXT_BEGINNING: builtins.int
ENGINE_TYPE_LANG: builtins.str
ENGINE_TYPE_SHAPE: builtins.str
GLYPH_EMPTY: builtins.int
GLYPH_INVALID_INPUT: builtins.int
GLYPH_UNKNOWN_FLAG: builtins.int
RENDER_TYPE_NONE: builtins.str
SCALE: builtins.int
UNKNOWN_GLYPH_HEIGHT: builtins.int
UNKNOWN_GLYPH_WIDTH: builtins.int
VERSION_MIN_REQUIRED: builtins.int
