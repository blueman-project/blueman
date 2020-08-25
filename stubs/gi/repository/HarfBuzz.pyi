import builtins
import typing

from gi.repository import GLib
from gi.repository import GObject


class blob_t():
    ...


class buffer_t():
    ...


class face_t():
    ...


class feature_t():
    end: builtins.int
    start: builtins.int
    tag: builtins.int
    value: builtins.int


class font_extents_t():
    ascender: builtins.int
    descender: builtins.int
    line_gap: builtins.int
    reserved1: builtins.int
    reserved2: builtins.int
    reserved3: builtins.int
    reserved4: builtins.int
    reserved5: builtins.int
    reserved6: builtins.int
    reserved7: builtins.int
    reserved8: builtins.int
    reserved9: builtins.int


class font_funcs_t():
    ...


class font_t():
    ...


class glyph_extents_t():
    height: builtins.int
    width: builtins.int
    x_bearing: builtins.int
    y_bearing: builtins.int


class glyph_info_t():
    cluster: builtins.int
    codepoint: builtins.int
    mask: builtins.int
    var1: var_int_t
    var2: var_int_t


class glyph_position_t():
    var: var_int_t
    x_advance: builtins.int
    x_offset: builtins.int
    y_advance: builtins.int
    y_offset: builtins.int


class language_t():
    ...


class map_t():
    ...


class ot_color_layer_t():
    color_index: builtins.int
    glyph: builtins.int


class ot_math_glyph_part_t():
    end_connector_length: builtins.int
    flags: ot_math_glyph_part_flags_t
    full_advance: builtins.int
    glyph: builtins.int
    start_connector_length: builtins.int


class ot_math_glyph_variant_t():
    advance: builtins.int
    glyph: builtins.int


class ot_name_entry_t():
    language: language_t
    name_id: builtins.int
    var: var_int_t


class ot_var_axis_info_t():
    axis_index: builtins.int
    default_value: builtins.float
    flags: ot_var_axis_flags_t
    max_value: builtins.float
    min_value: builtins.float
    name_id: builtins.int
    reserved: builtins.int
    tag: builtins.int


class ot_var_axis_t():
    default_value: builtins.float
    max_value: builtins.float
    min_value: builtins.float
    name_id: builtins.int
    tag: builtins.int


class segment_properties_t():
    direction: direction_t
    language: language_t
    reserved1: builtins.object
    reserved2: builtins.object
    script: script_t


class set_t():
    ...


class shape_plan_t():
    ...


class unicode_funcs_t():
    ...


class user_data_key_t():
    unused: builtins.int


class variation_t():
    tag: builtins.int
    value: builtins.float


class var_int_t():
    i16: typing.Sequence[builtins.int]
    i32: builtins.int
    i8: typing.Sequence[builtins.int]
    u16: typing.Sequence[builtins.int]
    u32: builtins.int
    u8: bytes


class buffer_diff_flags_t(GObject.GFlags, builtins.int):
    CLUSTER_MISMATCH = ...  # type: buffer_diff_flags_t
    CODEPOINT_MISMATCH = ...  # type: buffer_diff_flags_t
    CONTENT_TYPE_MISMATCH = ...  # type: buffer_diff_flags_t
    DOTTED_CIRCLE_PRESENT = ...  # type: buffer_diff_flags_t
    EQUAL = ...  # type: buffer_diff_flags_t
    GLYPH_FLAGS_MISMATCH = ...  # type: buffer_diff_flags_t
    LENGTH_MISMATCH = ...  # type: buffer_diff_flags_t
    NOTDEF_PRESENT = ...  # type: buffer_diff_flags_t
    POSITION_MISMATCH = ...  # type: buffer_diff_flags_t


class buffer_flags_t(GObject.GFlags, builtins.int):
    BOT = ...  # type: buffer_flags_t
    DEFAULT = ...  # type: buffer_flags_t
    DO_NOT_INSERT_DOTTED_CIRCLE = ...  # type: buffer_flags_t
    EOT = ...  # type: buffer_flags_t
    PRESERVE_DEFAULT_IGNORABLES = ...  # type: buffer_flags_t
    REMOVE_DEFAULT_IGNORABLES = ...  # type: buffer_flags_t


class buffer_serialize_flags_t(GObject.GFlags, builtins.int):
    DEFAULT = ...  # type: buffer_serialize_flags_t
    GLYPH_EXTENTS = ...  # type: buffer_serialize_flags_t
    GLYPH_FLAGS = ...  # type: buffer_serialize_flags_t
    NO_ADVANCES = ...  # type: buffer_serialize_flags_t
    NO_CLUSTERS = ...  # type: buffer_serialize_flags_t
    NO_GLYPH_NAMES = ...  # type: buffer_serialize_flags_t
    NO_POSITIONS = ...  # type: buffer_serialize_flags_t


class glyph_flags_t(GObject.GFlags, builtins.int):
    DEFINED = ...  # type: glyph_flags_t
    UNSAFE_TO_BREAK = ...  # type: glyph_flags_t


class ot_color_palette_flags_t(GObject.GFlags, builtins.int):
    DEFAULT = ...  # type: ot_color_palette_flags_t
    USABLE_WITH_DARK_BACKGROUND = ...  # type: ot_color_palette_flags_t
    USABLE_WITH_LIGHT_BACKGROUND = ...  # type: ot_color_palette_flags_t


class ot_math_glyph_part_flags_t(GObject.GFlags, builtins.int):
    EXTENDER = ...  # type: ot_math_glyph_part_flags_t


class ot_var_axis_flags_t(GObject.GFlags, builtins.int):
    HIDDEN = ...  # type: ot_var_axis_flags_t


class aat_layout_feature_selector_t(GObject.GEnum, builtins.int):
    ABBREV_SQUARED_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    ABBREV_SQUARED_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    ALL_CAPS = ...  # type: aat_layout_feature_selector_t
    ALL_LOWER_CASE = ...  # type: aat_layout_feature_selector_t
    ALL_TYPE_FEATURES_OFF = ...  # type: aat_layout_feature_selector_t
    ALL_TYPE_FEATURES_ON = ...  # type: aat_layout_feature_selector_t
    ALTERNATE_HORIZ_KANA_OFF = ...  # type: aat_layout_feature_selector_t
    ALTERNATE_HORIZ_KANA_ON = ...  # type: aat_layout_feature_selector_t
    ALTERNATE_VERT_KANA_OFF = ...  # type: aat_layout_feature_selector_t
    ALTERNATE_VERT_KANA_ON = ...  # type: aat_layout_feature_selector_t
    ALT_HALF_WIDTH_TEXT = ...  # type: aat_layout_feature_selector_t
    ALT_PROPORTIONAL_TEXT = ...  # type: aat_layout_feature_selector_t
    ASTERISK_TO_MULTIPLY_OFF = ...  # type: aat_layout_feature_selector_t
    ASTERISK_TO_MULTIPLY_ON = ...  # type: aat_layout_feature_selector_t
    BOX_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    CANONICAL_COMPOSITION_OFF = ...  # type: aat_layout_feature_selector_t
    CANONICAL_COMPOSITION_ON = ...  # type: aat_layout_feature_selector_t
    CASE_SENSITIVE_LAYOUT_OFF = ...  # type: aat_layout_feature_selector_t
    CASE_SENSITIVE_LAYOUT_ON = ...  # type: aat_layout_feature_selector_t
    CASE_SENSITIVE_SPACING_OFF = ...  # type: aat_layout_feature_selector_t
    CASE_SENSITIVE_SPACING_ON = ...  # type: aat_layout_feature_selector_t
    CIRCLE_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    CJK_ITALIC_ROMAN = ...  # type: aat_layout_feature_selector_t
    CJK_ITALIC_ROMAN_OFF = ...  # type: aat_layout_feature_selector_t
    CJK_ITALIC_ROMAN_ON = ...  # type: aat_layout_feature_selector_t
    CJK_SYMBOL_ALT_FIVE = ...  # type: aat_layout_feature_selector_t
    CJK_SYMBOL_ALT_FOUR = ...  # type: aat_layout_feature_selector_t
    CJK_SYMBOL_ALT_ONE = ...  # type: aat_layout_feature_selector_t
    CJK_SYMBOL_ALT_THREE = ...  # type: aat_layout_feature_selector_t
    CJK_SYMBOL_ALT_TWO = ...  # type: aat_layout_feature_selector_t
    CJK_VERTICAL_ROMAN_CENTERED = ...  # type: aat_layout_feature_selector_t
    CJK_VERTICAL_ROMAN_HBASELINE = ...  # type: aat_layout_feature_selector_t
    COMMON_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    COMMON_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    COMPATIBILITY_COMPOSITION_OFF = ...  # type: aat_layout_feature_selector_t
    COMPATIBILITY_COMPOSITION_ON = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_ALTERNATES_OFF = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_ALTERNATES_ON = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_SWASH_ALTERNATES_OFF = ...  # type: aat_layout_feature_selector_t
    CONTEXTUAL_SWASH_ALTERNATES_ON = ...  # type: aat_layout_feature_selector_t
    CURSIVE = ...  # type: aat_layout_feature_selector_t
    DECOMPOSE_DIACRITICS = ...  # type: aat_layout_feature_selector_t
    DECORATIVE_BORDERS = ...  # type: aat_layout_feature_selector_t
    DEFAULT_CJK_ROMAN = ...  # type: aat_layout_feature_selector_t
    DEFAULT_LOWER_CASE = ...  # type: aat_layout_feature_selector_t
    DEFAULT_UPPER_CASE = ...  # type: aat_layout_feature_selector_t
    DESIGN_LEVEL1 = ...  # type: aat_layout_feature_selector_t
    DESIGN_LEVEL2 = ...  # type: aat_layout_feature_selector_t
    DESIGN_LEVEL3 = ...  # type: aat_layout_feature_selector_t
    DESIGN_LEVEL4 = ...  # type: aat_layout_feature_selector_t
    DESIGN_LEVEL5 = ...  # type: aat_layout_feature_selector_t
    DIAGONAL_FRACTIONS = ...  # type: aat_layout_feature_selector_t
    DIAMOND_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    DINGBATS = ...  # type: aat_layout_feature_selector_t
    DIPHTHONG_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    DIPHTHONG_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    DISPLAY_TEXT = ...  # type: aat_layout_feature_selector_t
    ENGRAVED_TEXT = ...  # type: aat_layout_feature_selector_t
    EXPERT_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    EXPONENTS_OFF = ...  # type: aat_layout_feature_selector_t
    EXPONENTS_ON = ...  # type: aat_layout_feature_selector_t
    FLEURONS = ...  # type: aat_layout_feature_selector_t
    FORM_INTERROBANG_OFF = ...  # type: aat_layout_feature_selector_t
    FORM_INTERROBANG_ON = ...  # type: aat_layout_feature_selector_t
    FULL_WIDTH_CJK_ROMAN = ...  # type: aat_layout_feature_selector_t
    FULL_WIDTH_IDEOGRAPHS = ...  # type: aat_layout_feature_selector_t
    FULL_WIDTH_KANA = ...  # type: aat_layout_feature_selector_t
    HALF_WIDTH_CJK_ROMAN = ...  # type: aat_layout_feature_selector_t
    HALF_WIDTH_IDEOGRAPHS = ...  # type: aat_layout_feature_selector_t
    HALF_WIDTH_TEXT = ...  # type: aat_layout_feature_selector_t
    HANJA_TO_HANGUL = ...  # type: aat_layout_feature_selector_t
    HANJA_TO_HANGUL_ALT_ONE = ...  # type: aat_layout_feature_selector_t
    HANJA_TO_HANGUL_ALT_THREE = ...  # type: aat_layout_feature_selector_t
    HANJA_TO_HANGUL_ALT_TWO = ...  # type: aat_layout_feature_selector_t
    HIDE_DIACRITICS = ...  # type: aat_layout_feature_selector_t
    HIRAGANA_TO_KATAKANA = ...  # type: aat_layout_feature_selector_t
    HISTORICAL_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    HISTORICAL_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    HOJO_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    HYPHENS_TO_EM_DASH_OFF = ...  # type: aat_layout_feature_selector_t
    HYPHENS_TO_EM_DASH_ON = ...  # type: aat_layout_feature_selector_t
    HYPHEN_TO_EN_DASH_OFF = ...  # type: aat_layout_feature_selector_t
    HYPHEN_TO_EN_DASH_ON = ...  # type: aat_layout_feature_selector_t
    HYPHEN_TO_MINUS_OFF = ...  # type: aat_layout_feature_selector_t
    HYPHEN_TO_MINUS_ON = ...  # type: aat_layout_feature_selector_t
    IDEOGRAPHIC_ALT_FIVE = ...  # type: aat_layout_feature_selector_t
    IDEOGRAPHIC_ALT_FOUR = ...  # type: aat_layout_feature_selector_t
    IDEOGRAPHIC_ALT_ONE = ...  # type: aat_layout_feature_selector_t
    IDEOGRAPHIC_ALT_THREE = ...  # type: aat_layout_feature_selector_t
    IDEOGRAPHIC_ALT_TWO = ...  # type: aat_layout_feature_selector_t
    ILLUMINATED_CAPS = ...  # type: aat_layout_feature_selector_t
    INEQUALITY_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    INEQUALITY_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    INFERIORS = ...  # type: aat_layout_feature_selector_t
    INITIAL_CAPS = ...  # type: aat_layout_feature_selector_t
    INITIAL_CAPS_AND_SMALL_CAPS = ...  # type: aat_layout_feature_selector_t
    INTERNATIONAL_SYMBOLS = ...  # type: aat_layout_feature_selector_t
    INVALID = ...  # type: aat_layout_feature_selector_t
    INVERTED_BOX_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    INVERTED_CIRCLE_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    INVERTED_ROUNDED_BOX_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    JIS1978_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    JIS1983_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    JIS1990_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    JIS2004_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    KANA_TO_ROMANIZATION = ...  # type: aat_layout_feature_selector_t
    KATAKANA_TO_HIRAGANA = ...  # type: aat_layout_feature_selector_t
    LINE_FINAL_SWASHES_OFF = ...  # type: aat_layout_feature_selector_t
    LINE_FINAL_SWASHES_ON = ...  # type: aat_layout_feature_selector_t
    LINE_INITIAL_SWASHES_OFF = ...  # type: aat_layout_feature_selector_t
    LINE_INITIAL_SWASHES_ON = ...  # type: aat_layout_feature_selector_t
    LINGUISTIC_REARRANGEMENT_OFF = ...  # type: aat_layout_feature_selector_t
    LINGUISTIC_REARRANGEMENT_ON = ...  # type: aat_layout_feature_selector_t
    LOGOS_OFF = ...  # type: aat_layout_feature_selector_t
    LOGOS_ON = ...  # type: aat_layout_feature_selector_t
    LOWER_CASE_NUMBERS = ...  # type: aat_layout_feature_selector_t
    LOWER_CASE_PETITE_CAPS = ...  # type: aat_layout_feature_selector_t
    LOWER_CASE_SMALL_CAPS = ...  # type: aat_layout_feature_selector_t
    MATHEMATICAL_GREEK_OFF = ...  # type: aat_layout_feature_selector_t
    MATHEMATICAL_GREEK_ON = ...  # type: aat_layout_feature_selector_t
    MATH_SYMBOLS = ...  # type: aat_layout_feature_selector_t
    MONOSPACED_NUMBERS = ...  # type: aat_layout_feature_selector_t
    MONOSPACED_TEXT = ...  # type: aat_layout_feature_selector_t
    NLCCHARACTERS = ...  # type: aat_layout_feature_selector_t
    NON_FINAL_SWASHES_OFF = ...  # type: aat_layout_feature_selector_t
    NON_FINAL_SWASHES_ON = ...  # type: aat_layout_feature_selector_t
    NORMAL_POSITION = ...  # type: aat_layout_feature_selector_t
    NO_ALTERNATES = ...  # type: aat_layout_feature_selector_t
    NO_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    NO_CJK_ITALIC_ROMAN = ...  # type: aat_layout_feature_selector_t
    NO_CJK_SYMBOL_ALTERNATIVES = ...  # type: aat_layout_feature_selector_t
    NO_FRACTIONS = ...  # type: aat_layout_feature_selector_t
    NO_IDEOGRAPHIC_ALTERNATIVES = ...  # type: aat_layout_feature_selector_t
    NO_ORNAMENTS = ...  # type: aat_layout_feature_selector_t
    NO_RUBY_KANA = ...  # type: aat_layout_feature_selector_t
    NO_STYLE_OPTIONS = ...  # type: aat_layout_feature_selector_t
    NO_STYLISTIC_ALTERNATES = ...  # type: aat_layout_feature_selector_t
    NO_TRANSLITERATION = ...  # type: aat_layout_feature_selector_t
    ORDINALS = ...  # type: aat_layout_feature_selector_t
    PARENTHESIS_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    PARTIALLY_CONNECTED = ...  # type: aat_layout_feature_selector_t
    PERIODS_TO_ELLIPSIS_OFF = ...  # type: aat_layout_feature_selector_t
    PERIODS_TO_ELLIPSIS_ON = ...  # type: aat_layout_feature_selector_t
    PERIOD_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    PI_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    PREVENT_OVERLAP_OFF = ...  # type: aat_layout_feature_selector_t
    PREVENT_OVERLAP_ON = ...  # type: aat_layout_feature_selector_t
    PROPORTIONAL_CJK_ROMAN = ...  # type: aat_layout_feature_selector_t
    PROPORTIONAL_IDEOGRAPHS = ...  # type: aat_layout_feature_selector_t
    PROPORTIONAL_KANA = ...  # type: aat_layout_feature_selector_t
    PROPORTIONAL_NUMBERS = ...  # type: aat_layout_feature_selector_t
    PROPORTIONAL_TEXT = ...  # type: aat_layout_feature_selector_t
    QUARTER_WIDTH_NUMBERS = ...  # type: aat_layout_feature_selector_t
    QUARTER_WIDTH_TEXT = ...  # type: aat_layout_feature_selector_t
    RARE_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    RARE_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    REBUS_PICTURES_OFF = ...  # type: aat_layout_feature_selector_t
    REBUS_PICTURES_ON = ...  # type: aat_layout_feature_selector_t
    REQUIRED_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    REQUIRED_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    ROMANIZATION_TO_HIRAGANA = ...  # type: aat_layout_feature_selector_t
    ROMANIZATION_TO_KATAKANA = ...  # type: aat_layout_feature_selector_t
    ROMAN_NUMERAL_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    ROUNDED_BOX_ANNOTATION = ...  # type: aat_layout_feature_selector_t
    RUBY_KANA = ...  # type: aat_layout_feature_selector_t
    RUBY_KANA_OFF = ...  # type: aat_layout_feature_selector_t
    RUBY_KANA_ON = ...  # type: aat_layout_feature_selector_t
    SCIENTIFIC_INFERIORS = ...  # type: aat_layout_feature_selector_t
    SHOW_DIACRITICS = ...  # type: aat_layout_feature_selector_t
    SIMPLIFIED_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    SLASHED_ZERO_OFF = ...  # type: aat_layout_feature_selector_t
    SLASHED_ZERO_ON = ...  # type: aat_layout_feature_selector_t
    SLASH_TO_DIVIDE_OFF = ...  # type: aat_layout_feature_selector_t
    SLASH_TO_DIVIDE_ON = ...  # type: aat_layout_feature_selector_t
    SMALL_CAPS = ...  # type: aat_layout_feature_selector_t
    SMART_QUOTES_OFF = ...  # type: aat_layout_feature_selector_t
    SMART_QUOTES_ON = ...  # type: aat_layout_feature_selector_t
    SQUARED_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    SQUARED_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_EIGHTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_EIGHTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_EIGHT_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_EIGHT_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_ELEVEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_ELEVEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FIFTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FIFTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FIVE_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FIVE_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FOURTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FOURTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FOUR_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_FOUR_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_NINETEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_NINETEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_NINE_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_NINE_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_ONE_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_ONE_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SEVENTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SEVENTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SEVEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SEVEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SIXTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SIXTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SIX_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_SIX_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_THIRTEEN_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_THIRTEEN_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_THREE_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_THREE_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWELVE_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWELVE_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWENTY_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWENTY_ON = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWO_OFF = ...  # type: aat_layout_feature_selector_t
    STYLISTIC_ALT_TWO_ON = ...  # type: aat_layout_feature_selector_t
    SUBSTITUTE_VERTICAL_FORMS_OFF = ...  # type: aat_layout_feature_selector_t
    SUBSTITUTE_VERTICAL_FORMS_ON = ...  # type: aat_layout_feature_selector_t
    SUPERIORS = ...  # type: aat_layout_feature_selector_t
    SWASH_ALTERNATES_OFF = ...  # type: aat_layout_feature_selector_t
    SWASH_ALTERNATES_ON = ...  # type: aat_layout_feature_selector_t
    SYMBOL_LIGATURES_OFF = ...  # type: aat_layout_feature_selector_t
    SYMBOL_LIGATURES_ON = ...  # type: aat_layout_feature_selector_t
    TALL_CAPS = ...  # type: aat_layout_feature_selector_t
    THIRD_WIDTH_NUMBERS = ...  # type: aat_layout_feature_selector_t
    THIRD_WIDTH_TEXT = ...  # type: aat_layout_feature_selector_t
    TITLING_CAPS = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_ALT_FIVE = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_ALT_FOUR = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_ALT_ONE = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_ALT_THREE = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_ALT_TWO = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    TRADITIONAL_NAMES_CHARACTERS = ...  # type: aat_layout_feature_selector_t
    TRANSCODING_COMPOSITION_OFF = ...  # type: aat_layout_feature_selector_t
    TRANSCODING_COMPOSITION_ON = ...  # type: aat_layout_feature_selector_t
    UNCONNECTED = ...  # type: aat_layout_feature_selector_t
    UPPER_AND_LOWER_CASE = ...  # type: aat_layout_feature_selector_t
    UPPER_CASE_NUMBERS = ...  # type: aat_layout_feature_selector_t
    UPPER_CASE_PETITE_CAPS = ...  # type: aat_layout_feature_selector_t
    UPPER_CASE_SMALL_CAPS = ...  # type: aat_layout_feature_selector_t
    VERTICAL_FRACTIONS = ...  # type: aat_layout_feature_selector_t
    WORD_FINAL_SWASHES_OFF = ...  # type: aat_layout_feature_selector_t
    WORD_FINAL_SWASHES_ON = ...  # type: aat_layout_feature_selector_t
    WORD_INITIAL_SWASHES_OFF = ...  # type: aat_layout_feature_selector_t
    WORD_INITIAL_SWASHES_ON = ...  # type: aat_layout_feature_selector_t


class aat_layout_feature_type_t(GObject.GEnum, builtins.int):
    ALL_TYPOGRAPHIC = ...  # type: aat_layout_feature_type_t
    ALTERNATE_KANA = ...  # type: aat_layout_feature_type_t
    ANNOTATION_TYPE = ...  # type: aat_layout_feature_type_t
    CASE_SENSITIVE_LAYOUT = ...  # type: aat_layout_feature_type_t
    CHARACTER_ALTERNATIVES = ...  # type: aat_layout_feature_type_t
    CHARACTER_SHAPE = ...  # type: aat_layout_feature_type_t
    CJK_ROMAN_SPACING_TYPE = ...  # type: aat_layout_feature_type_t
    CJK_SYMBOL_ALTERNATIVES_TYPE = ...  # type: aat_layout_feature_type_t
    CJK_VERTICAL_ROMAN_PLACEMENT_TYPE = ...  # type: aat_layout_feature_type_t
    CONTEXTUAL_ALTERNATIVES = ...  # type: aat_layout_feature_type_t
    CURISVE_CONNECTION = ...  # type: aat_layout_feature_type_t
    DESIGN_COMPLEXITY_TYPE = ...  # type: aat_layout_feature_type_t
    DIACRITICS_TYPE = ...  # type: aat_layout_feature_type_t
    FRACTIONS = ...  # type: aat_layout_feature_type_t
    IDEOGRAPHIC_ALTERNATIVES_TYPE = ...  # type: aat_layout_feature_type_t
    IDEOGRAPHIC_SPACING_TYPE = ...  # type: aat_layout_feature_type_t
    INVALID = ...  # type: aat_layout_feature_type_t
    ITALIC_CJK_ROMAN = ...  # type: aat_layout_feature_type_t
    KANA_SPACING_TYPE = ...  # type: aat_layout_feature_type_t
    LANGUAGE_TAG_TYPE = ...  # type: aat_layout_feature_type_t
    LETTER_CASE = ...  # type: aat_layout_feature_type_t
    LIGATURES = ...  # type: aat_layout_feature_type_t
    LINGUISTIC_REARRANGEMENT = ...  # type: aat_layout_feature_type_t
    LOWER_CASE = ...  # type: aat_layout_feature_type_t
    MATHEMATICAL_EXTRAS = ...  # type: aat_layout_feature_type_t
    NUMBER_CASE = ...  # type: aat_layout_feature_type_t
    NUMBER_SPACING = ...  # type: aat_layout_feature_type_t
    ORNAMENT_SETS_TYPE = ...  # type: aat_layout_feature_type_t
    OVERLAPPING_CHARACTERS_TYPE = ...  # type: aat_layout_feature_type_t
    RUBY_KANA = ...  # type: aat_layout_feature_type_t
    SMART_SWASH_TYPE = ...  # type: aat_layout_feature_type_t
    STYLE_OPTIONS = ...  # type: aat_layout_feature_type_t
    STYLISTIC_ALTERNATIVES = ...  # type: aat_layout_feature_type_t
    TEXT_SPACING = ...  # type: aat_layout_feature_type_t
    TRANSLITERATION = ...  # type: aat_layout_feature_type_t
    TYPOGRAPHIC_EXTRAS = ...  # type: aat_layout_feature_type_t
    UNICODE_DECOMPOSITION_TYPE = ...  # type: aat_layout_feature_type_t
    UPPER_CASE = ...  # type: aat_layout_feature_type_t
    VERTICAL_POSITION = ...  # type: aat_layout_feature_type_t
    VERTICAL_SUBSTITUTION = ...  # type: aat_layout_feature_type_t


class buffer_cluster_level_t(GObject.GEnum, builtins.int):
    CHARACTERS = ...  # type: buffer_cluster_level_t
    DEFAULT = ...  # type: buffer_cluster_level_t
    MONOTONE_CHARACTERS = ...  # type: buffer_cluster_level_t
    MONOTONE_GRAPHEMES = ...  # type: buffer_cluster_level_t


class buffer_content_type_t(GObject.GEnum, builtins.int):
    GLYPHS = ...  # type: buffer_content_type_t
    INVALID = ...  # type: buffer_content_type_t
    UNICODE = ...  # type: buffer_content_type_t


class buffer_serialize_format_t(GObject.GEnum, builtins.int):
    INVALID = ...  # type: buffer_serialize_format_t
    JSON = ...  # type: buffer_serialize_format_t
    TEXT = ...  # type: buffer_serialize_format_t


class direction_t(GObject.GEnum, builtins.int):
    BTT = ...  # type: direction_t
    INVALID = ...  # type: direction_t
    LTR = ...  # type: direction_t
    RTL = ...  # type: direction_t
    TTB = ...  # type: direction_t


class memory_mode_t(GObject.GEnum, builtins.int):
    DUPLICATE = ...  # type: memory_mode_t
    READONLY = ...  # type: memory_mode_t
    READONLY_MAY_MAKE_WRITABLE = ...  # type: memory_mode_t
    WRITABLE = ...  # type: memory_mode_t


class ot_layout_baseline_tag_t(GObject.GEnum, builtins.int):
    HANGING = ...  # type: ot_layout_baseline_tag_t
    IDEO_EMBOX_BOTTOM_OR_LEFT = ...  # type: ot_layout_baseline_tag_t
    IDEO_EMBOX_TOP_OR_RIGHT = ...  # type: ot_layout_baseline_tag_t
    IDEO_FACE_BOTTOM_OR_LEFT = ...  # type: ot_layout_baseline_tag_t
    IDEO_FACE_TOP_OR_RIGHT = ...  # type: ot_layout_baseline_tag_t
    MATH = ...  # type: ot_layout_baseline_tag_t
    ROMAN = ...  # type: ot_layout_baseline_tag_t


class ot_layout_glyph_class_t(GObject.GEnum, builtins.int):
    BASE_GLYPH = ...  # type: ot_layout_glyph_class_t
    COMPONENT = ...  # type: ot_layout_glyph_class_t
    LIGATURE = ...  # type: ot_layout_glyph_class_t
    MARK = ...  # type: ot_layout_glyph_class_t
    UNCLASSIFIED = ...  # type: ot_layout_glyph_class_t


class ot_math_constant_t(GObject.GEnum, builtins.int):
    ACCENT_BASE_HEIGHT = ...  # type: ot_math_constant_t
    AXIS_HEIGHT = ...  # type: ot_math_constant_t
    DELIMITED_SUB_FORMULA_MIN_HEIGHT = ...  # type: ot_math_constant_t
    DISPLAY_OPERATOR_MIN_HEIGHT = ...  # type: ot_math_constant_t
    FLATTENED_ACCENT_BASE_HEIGHT = ...  # type: ot_math_constant_t
    FRACTION_DENOMINATOR_DISPLAY_STYLE_SHIFT_DOWN = ...  # type: ot_math_constant_t
    FRACTION_DENOMINATOR_GAP_MIN = ...  # type: ot_math_constant_t
    FRACTION_DENOMINATOR_SHIFT_DOWN = ...  # type: ot_math_constant_t
    FRACTION_DENOM_DISPLAY_STYLE_GAP_MIN = ...  # type: ot_math_constant_t
    FRACTION_NUMERATOR_DISPLAY_STYLE_SHIFT_UP = ...  # type: ot_math_constant_t
    FRACTION_NUMERATOR_GAP_MIN = ...  # type: ot_math_constant_t
    FRACTION_NUMERATOR_SHIFT_UP = ...  # type: ot_math_constant_t
    FRACTION_NUM_DISPLAY_STYLE_GAP_MIN = ...  # type: ot_math_constant_t
    FRACTION_RULE_THICKNESS = ...  # type: ot_math_constant_t
    LOWER_LIMIT_BASELINE_DROP_MIN = ...  # type: ot_math_constant_t
    LOWER_LIMIT_GAP_MIN = ...  # type: ot_math_constant_t
    MATH_LEADING = ...  # type: ot_math_constant_t
    OVERBAR_EXTRA_ASCENDER = ...  # type: ot_math_constant_t
    OVERBAR_RULE_THICKNESS = ...  # type: ot_math_constant_t
    OVERBAR_VERTICAL_GAP = ...  # type: ot_math_constant_t
    RADICAL_DEGREE_BOTTOM_RAISE_PERCENT = ...  # type: ot_math_constant_t
    RADICAL_DISPLAY_STYLE_VERTICAL_GAP = ...  # type: ot_math_constant_t
    RADICAL_EXTRA_ASCENDER = ...  # type: ot_math_constant_t
    RADICAL_KERN_AFTER_DEGREE = ...  # type: ot_math_constant_t
    RADICAL_KERN_BEFORE_DEGREE = ...  # type: ot_math_constant_t
    RADICAL_RULE_THICKNESS = ...  # type: ot_math_constant_t
    RADICAL_VERTICAL_GAP = ...  # type: ot_math_constant_t
    SCRIPT_PERCENT_SCALE_DOWN = ...  # type: ot_math_constant_t
    SCRIPT_SCRIPT_PERCENT_SCALE_DOWN = ...  # type: ot_math_constant_t
    SKEWED_FRACTION_HORIZONTAL_GAP = ...  # type: ot_math_constant_t
    SKEWED_FRACTION_VERTICAL_GAP = ...  # type: ot_math_constant_t
    SPACE_AFTER_SCRIPT = ...  # type: ot_math_constant_t
    STACK_BOTTOM_DISPLAY_STYLE_SHIFT_DOWN = ...  # type: ot_math_constant_t
    STACK_BOTTOM_SHIFT_DOWN = ...  # type: ot_math_constant_t
    STACK_DISPLAY_STYLE_GAP_MIN = ...  # type: ot_math_constant_t
    STACK_GAP_MIN = ...  # type: ot_math_constant_t
    STACK_TOP_DISPLAY_STYLE_SHIFT_UP = ...  # type: ot_math_constant_t
    STACK_TOP_SHIFT_UP = ...  # type: ot_math_constant_t
    STRETCH_STACK_BOTTOM_SHIFT_DOWN = ...  # type: ot_math_constant_t
    STRETCH_STACK_GAP_ABOVE_MIN = ...  # type: ot_math_constant_t
    STRETCH_STACK_GAP_BELOW_MIN = ...  # type: ot_math_constant_t
    STRETCH_STACK_TOP_SHIFT_UP = ...  # type: ot_math_constant_t
    SUBSCRIPT_BASELINE_DROP_MIN = ...  # type: ot_math_constant_t
    SUBSCRIPT_SHIFT_DOWN = ...  # type: ot_math_constant_t
    SUBSCRIPT_TOP_MAX = ...  # type: ot_math_constant_t
    SUB_SUPERSCRIPT_GAP_MIN = ...  # type: ot_math_constant_t
    SUPERSCRIPT_BASELINE_DROP_MAX = ...  # type: ot_math_constant_t
    SUPERSCRIPT_BOTTOM_MAX_WITH_SUBSCRIPT = ...  # type: ot_math_constant_t
    SUPERSCRIPT_BOTTOM_MIN = ...  # type: ot_math_constant_t
    SUPERSCRIPT_SHIFT_UP = ...  # type: ot_math_constant_t
    SUPERSCRIPT_SHIFT_UP_CRAMPED = ...  # type: ot_math_constant_t
    UNDERBAR_EXTRA_DESCENDER = ...  # type: ot_math_constant_t
    UNDERBAR_RULE_THICKNESS = ...  # type: ot_math_constant_t
    UNDERBAR_VERTICAL_GAP = ...  # type: ot_math_constant_t
    UPPER_LIMIT_BASELINE_RISE_MIN = ...  # type: ot_math_constant_t
    UPPER_LIMIT_GAP_MIN = ...  # type: ot_math_constant_t


class ot_math_kern_t(GObject.GEnum, builtins.int):
    BOTTOM_LEFT = ...  # type: ot_math_kern_t
    BOTTOM_RIGHT = ...  # type: ot_math_kern_t
    TOP_LEFT = ...  # type: ot_math_kern_t
    TOP_RIGHT = ...  # type: ot_math_kern_t


class ot_meta_tag_t(GObject.GEnum, builtins.int):
    DESIGN_LANGUAGES = ...  # type: ot_meta_tag_t
    SUPPORTED_LANGUAGES = ...  # type: ot_meta_tag_t


class ot_metrics_tag_t(GObject.GEnum, builtins.int):
    CAP_HEIGHT = ...  # type: ot_metrics_tag_t
    HORIZONTAL_ASCENDER = ...  # type: ot_metrics_tag_t
    HORIZONTAL_CARET_OFFSET = ...  # type: ot_metrics_tag_t
    HORIZONTAL_CARET_RISE = ...  # type: ot_metrics_tag_t
    HORIZONTAL_CARET_RUN = ...  # type: ot_metrics_tag_t
    HORIZONTAL_CLIPPING_ASCENT = ...  # type: ot_metrics_tag_t
    HORIZONTAL_CLIPPING_DESCENT = ...  # type: ot_metrics_tag_t
    HORIZONTAL_DESCENDER = ...  # type: ot_metrics_tag_t
    HORIZONTAL_LINE_GAP = ...  # type: ot_metrics_tag_t
    STRIKEOUT_OFFSET = ...  # type: ot_metrics_tag_t
    STRIKEOUT_SIZE = ...  # type: ot_metrics_tag_t
    SUBSCRIPT_EM_X_OFFSET = ...  # type: ot_metrics_tag_t
    SUBSCRIPT_EM_X_SIZE = ...  # type: ot_metrics_tag_t
    SUBSCRIPT_EM_Y_OFFSET = ...  # type: ot_metrics_tag_t
    SUBSCRIPT_EM_Y_SIZE = ...  # type: ot_metrics_tag_t
    SUPERSCRIPT_EM_X_OFFSET = ...  # type: ot_metrics_tag_t
    SUPERSCRIPT_EM_X_SIZE = ...  # type: ot_metrics_tag_t
    SUPERSCRIPT_EM_Y_OFFSET = ...  # type: ot_metrics_tag_t
    SUPERSCRIPT_EM_Y_SIZE = ...  # type: ot_metrics_tag_t
    UNDERLINE_OFFSET = ...  # type: ot_metrics_tag_t
    UNDERLINE_SIZE = ...  # type: ot_metrics_tag_t
    VERTICAL_ASCENDER = ...  # type: ot_metrics_tag_t
    VERTICAL_CARET_OFFSET = ...  # type: ot_metrics_tag_t
    VERTICAL_CARET_RISE = ...  # type: ot_metrics_tag_t
    VERTICAL_CARET_RUN = ...  # type: ot_metrics_tag_t
    VERTICAL_DESCENDER = ...  # type: ot_metrics_tag_t
    VERTICAL_LINE_GAP = ...  # type: ot_metrics_tag_t
    X_HEIGHT = ...  # type: ot_metrics_tag_t


class script_t(GObject.GEnum, builtins.int):
    ADLAM = ...  # type: script_t
    AHOM = ...  # type: script_t
    ANATOLIAN_HIEROGLYPHS = ...  # type: script_t
    ARABIC = ...  # type: script_t
    ARMENIAN = ...  # type: script_t
    AVESTAN = ...  # type: script_t
    BALINESE = ...  # type: script_t
    BAMUM = ...  # type: script_t
    BASSA_VAH = ...  # type: script_t
    BATAK = ...  # type: script_t
    BENGALI = ...  # type: script_t
    BHAIKSUKI = ...  # type: script_t
    BOPOMOFO = ...  # type: script_t
    BRAHMI = ...  # type: script_t
    BRAILLE = ...  # type: script_t
    BUGINESE = ...  # type: script_t
    BUHID = ...  # type: script_t
    CANADIAN_SYLLABICS = ...  # type: script_t
    CARIAN = ...  # type: script_t
    CAUCASIAN_ALBANIAN = ...  # type: script_t
    CHAKMA = ...  # type: script_t
    CHAM = ...  # type: script_t
    CHEROKEE = ...  # type: script_t
    CHORASMIAN = ...  # type: script_t
    COMMON = ...  # type: script_t
    COPTIC = ...  # type: script_t
    CUNEIFORM = ...  # type: script_t
    CYPRIOT = ...  # type: script_t
    CYRILLIC = ...  # type: script_t
    DESERET = ...  # type: script_t
    DEVANAGARI = ...  # type: script_t
    DIVES_AKURU = ...  # type: script_t
    DOGRA = ...  # type: script_t
    DUPLOYAN = ...  # type: script_t
    EGYPTIAN_HIEROGLYPHS = ...  # type: script_t
    ELBASAN = ...  # type: script_t
    ELYMAIC = ...  # type: script_t
    ETHIOPIC = ...  # type: script_t
    GEORGIAN = ...  # type: script_t
    GLAGOLITIC = ...  # type: script_t
    GOTHIC = ...  # type: script_t
    GRANTHA = ...  # type: script_t
    GREEK = ...  # type: script_t
    GUJARATI = ...  # type: script_t
    GUNJALA_GONDI = ...  # type: script_t
    GURMUKHI = ...  # type: script_t
    HAN = ...  # type: script_t
    HANGUL = ...  # type: script_t
    HANIFI_ROHINGYA = ...  # type: script_t
    HANUNOO = ...  # type: script_t
    HATRAN = ...  # type: script_t
    HEBREW = ...  # type: script_t
    HIRAGANA = ...  # type: script_t
    IMPERIAL_ARAMAIC = ...  # type: script_t
    INHERITED = ...  # type: script_t
    INSCRIPTIONAL_PAHLAVI = ...  # type: script_t
    INSCRIPTIONAL_PARTHIAN = ...  # type: script_t
    INVALID = ...  # type: script_t
    JAVANESE = ...  # type: script_t
    KAITHI = ...  # type: script_t
    KANNADA = ...  # type: script_t
    KATAKANA = ...  # type: script_t
    KAYAH_LI = ...  # type: script_t
    KHAROSHTHI = ...  # type: script_t
    KHITAN_SMALL_SCRIPT = ...  # type: script_t
    KHMER = ...  # type: script_t
    KHOJKI = ...  # type: script_t
    KHUDAWADI = ...  # type: script_t
    LAO = ...  # type: script_t
    LATIN = ...  # type: script_t
    LEPCHA = ...  # type: script_t
    LIMBU = ...  # type: script_t
    LINEAR_A = ...  # type: script_t
    LINEAR_B = ...  # type: script_t
    LISU = ...  # type: script_t
    LYCIAN = ...  # type: script_t
    LYDIAN = ...  # type: script_t
    MAHAJANI = ...  # type: script_t
    MAKASAR = ...  # type: script_t
    MALAYALAM = ...  # type: script_t
    MANDAIC = ...  # type: script_t
    MANICHAEAN = ...  # type: script_t
    MARCHEN = ...  # type: script_t
    MASARAM_GONDI = ...  # type: script_t
    MEDEFAIDRIN = ...  # type: script_t
    MEETEI_MAYEK = ...  # type: script_t
    MENDE_KIKAKUI = ...  # type: script_t
    MEROITIC_CURSIVE = ...  # type: script_t
    MEROITIC_HIEROGLYPHS = ...  # type: script_t
    MIAO = ...  # type: script_t
    MODI = ...  # type: script_t
    MONGOLIAN = ...  # type: script_t
    MRO = ...  # type: script_t
    MULTANI = ...  # type: script_t
    MYANMAR = ...  # type: script_t
    NABATAEAN = ...  # type: script_t
    NANDINAGARI = ...  # type: script_t
    NEWA = ...  # type: script_t
    NEW_TAI_LUE = ...  # type: script_t
    NKO = ...  # type: script_t
    NUSHU = ...  # type: script_t
    NYIAKENG_PUACHUE_HMONG = ...  # type: script_t
    OGHAM = ...  # type: script_t
    OLD_HUNGARIAN = ...  # type: script_t
    OLD_ITALIC = ...  # type: script_t
    OLD_NORTH_ARABIAN = ...  # type: script_t
    OLD_PERMIC = ...  # type: script_t
    OLD_PERSIAN = ...  # type: script_t
    OLD_SOGDIAN = ...  # type: script_t
    OLD_SOUTH_ARABIAN = ...  # type: script_t
    OLD_TURKIC = ...  # type: script_t
    OL_CHIKI = ...  # type: script_t
    ORIYA = ...  # type: script_t
    OSAGE = ...  # type: script_t
    OSMANYA = ...  # type: script_t
    PAHAWH_HMONG = ...  # type: script_t
    PALMYRENE = ...  # type: script_t
    PAU_CIN_HAU = ...  # type: script_t
    PHAGS_PA = ...  # type: script_t
    PHOENICIAN = ...  # type: script_t
    PSALTER_PAHLAVI = ...  # type: script_t
    REJANG = ...  # type: script_t
    RUNIC = ...  # type: script_t
    SAMARITAN = ...  # type: script_t
    SAURASHTRA = ...  # type: script_t
    SHARADA = ...  # type: script_t
    SHAVIAN = ...  # type: script_t
    SIDDHAM = ...  # type: script_t
    SIGNWRITING = ...  # type: script_t
    SINHALA = ...  # type: script_t
    SOGDIAN = ...  # type: script_t
    SORA_SOMPENG = ...  # type: script_t
    SOYOMBO = ...  # type: script_t
    SUNDANESE = ...  # type: script_t
    SYLOTI_NAGRI = ...  # type: script_t
    SYRIAC = ...  # type: script_t
    TAGALOG = ...  # type: script_t
    TAGBANWA = ...  # type: script_t
    TAI_LE = ...  # type: script_t
    TAI_THAM = ...  # type: script_t
    TAI_VIET = ...  # type: script_t
    TAKRI = ...  # type: script_t
    TAMIL = ...  # type: script_t
    TANGUT = ...  # type: script_t
    TELUGU = ...  # type: script_t
    THAANA = ...  # type: script_t
    THAI = ...  # type: script_t
    TIBETAN = ...  # type: script_t
    TIFINAGH = ...  # type: script_t
    TIRHUTA = ...  # type: script_t
    UGARITIC = ...  # type: script_t
    UNKNOWN = ...  # type: script_t
    VAI = ...  # type: script_t
    WANCHO = ...  # type: script_t
    WARANG_CITI = ...  # type: script_t
    YEZIDI = ...  # type: script_t
    YI = ...  # type: script_t
    ZANABAZAR_SQUARE = ...  # type: script_t


class unicode_combining_class_t(GObject.GEnum, builtins.int):
    ABOVE = ...  # type: unicode_combining_class_t
    ABOVE_LEFT = ...  # type: unicode_combining_class_t
    ABOVE_RIGHT = ...  # type: unicode_combining_class_t
    ATTACHED_ABOVE = ...  # type: unicode_combining_class_t
    ATTACHED_ABOVE_RIGHT = ...  # type: unicode_combining_class_t
    ATTACHED_BELOW = ...  # type: unicode_combining_class_t
    ATTACHED_BELOW_LEFT = ...  # type: unicode_combining_class_t
    BELOW = ...  # type: unicode_combining_class_t
    BELOW_LEFT = ...  # type: unicode_combining_class_t
    BELOW_RIGHT = ...  # type: unicode_combining_class_t
    CCC10 = ...  # type: unicode_combining_class_t
    CCC103 = ...  # type: unicode_combining_class_t
    CCC107 = ...  # type: unicode_combining_class_t
    CCC11 = ...  # type: unicode_combining_class_t
    CCC118 = ...  # type: unicode_combining_class_t
    CCC12 = ...  # type: unicode_combining_class_t
    CCC122 = ...  # type: unicode_combining_class_t
    CCC129 = ...  # type: unicode_combining_class_t
    CCC13 = ...  # type: unicode_combining_class_t
    CCC130 = ...  # type: unicode_combining_class_t
    CCC133 = ...  # type: unicode_combining_class_t
    CCC14 = ...  # type: unicode_combining_class_t
    CCC15 = ...  # type: unicode_combining_class_t
    CCC16 = ...  # type: unicode_combining_class_t
    CCC17 = ...  # type: unicode_combining_class_t
    CCC18 = ...  # type: unicode_combining_class_t
    CCC19 = ...  # type: unicode_combining_class_t
    CCC20 = ...  # type: unicode_combining_class_t
    CCC21 = ...  # type: unicode_combining_class_t
    CCC22 = ...  # type: unicode_combining_class_t
    CCC23 = ...  # type: unicode_combining_class_t
    CCC24 = ...  # type: unicode_combining_class_t
    CCC25 = ...  # type: unicode_combining_class_t
    CCC26 = ...  # type: unicode_combining_class_t
    CCC27 = ...  # type: unicode_combining_class_t
    CCC28 = ...  # type: unicode_combining_class_t
    CCC29 = ...  # type: unicode_combining_class_t
    CCC30 = ...  # type: unicode_combining_class_t
    CCC31 = ...  # type: unicode_combining_class_t
    CCC32 = ...  # type: unicode_combining_class_t
    CCC33 = ...  # type: unicode_combining_class_t
    CCC34 = ...  # type: unicode_combining_class_t
    CCC35 = ...  # type: unicode_combining_class_t
    CCC36 = ...  # type: unicode_combining_class_t
    CCC84 = ...  # type: unicode_combining_class_t
    CCC91 = ...  # type: unicode_combining_class_t
    DOUBLE_ABOVE = ...  # type: unicode_combining_class_t
    DOUBLE_BELOW = ...  # type: unicode_combining_class_t
    INVALID = ...  # type: unicode_combining_class_t
    IOTA_SUBSCRIPT = ...  # type: unicode_combining_class_t
    KANA_VOICING = ...  # type: unicode_combining_class_t
    LEFT = ...  # type: unicode_combining_class_t
    NOT_REORDERED = ...  # type: unicode_combining_class_t
    NUKTA = ...  # type: unicode_combining_class_t
    OVERLAY = ...  # type: unicode_combining_class_t
    RIGHT = ...  # type: unicode_combining_class_t
    VIRAMA = ...  # type: unicode_combining_class_t


class unicode_general_category_t(GObject.GEnum, builtins.int):
    CLOSE_PUNCTUATION = ...  # type: unicode_general_category_t
    CONNECT_PUNCTUATION = ...  # type: unicode_general_category_t
    CONTROL = ...  # type: unicode_general_category_t
    CURRENCY_SYMBOL = ...  # type: unicode_general_category_t
    DASH_PUNCTUATION = ...  # type: unicode_general_category_t
    DECIMAL_NUMBER = ...  # type: unicode_general_category_t
    ENCLOSING_MARK = ...  # type: unicode_general_category_t
    FINAL_PUNCTUATION = ...  # type: unicode_general_category_t
    FORMAT = ...  # type: unicode_general_category_t
    INITIAL_PUNCTUATION = ...  # type: unicode_general_category_t
    LETTER_NUMBER = ...  # type: unicode_general_category_t
    LINE_SEPARATOR = ...  # type: unicode_general_category_t
    LOWERCASE_LETTER = ...  # type: unicode_general_category_t
    MATH_SYMBOL = ...  # type: unicode_general_category_t
    MODIFIER_LETTER = ...  # type: unicode_general_category_t
    MODIFIER_SYMBOL = ...  # type: unicode_general_category_t
    NON_SPACING_MARK = ...  # type: unicode_general_category_t
    OPEN_PUNCTUATION = ...  # type: unicode_general_category_t
    OTHER_LETTER = ...  # type: unicode_general_category_t
    OTHER_NUMBER = ...  # type: unicode_general_category_t
    OTHER_PUNCTUATION = ...  # type: unicode_general_category_t
    OTHER_SYMBOL = ...  # type: unicode_general_category_t
    PARAGRAPH_SEPARATOR = ...  # type: unicode_general_category_t
    PRIVATE_USE = ...  # type: unicode_general_category_t
    SPACE_SEPARATOR = ...  # type: unicode_general_category_t
    SPACING_MARK = ...  # type: unicode_general_category_t
    SURROGATE = ...  # type: unicode_general_category_t
    TITLECASE_LETTER = ...  # type: unicode_general_category_t
    UNASSIGNED = ...  # type: unicode_general_category_t
    UPPERCASE_LETTER = ...  # type: unicode_general_category_t


buffer_message_func_t = typing.Callable[[buffer_t, font_t, builtins.str, typing.Optional[builtins.object]], builtins.int]
destroy_func_t = typing.Callable[[typing.Optional[builtins.object]], None]
font_get_font_extents_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], font_extents_t, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_advance_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_advances_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], None]
font_get_glyph_contour_point_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_extents_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, glyph_extents_t, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_from_name_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.str, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_kerning_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_name_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.str, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_glyph_origin_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_nominal_glyph_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_nominal_glyphs_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
font_get_variation_glyph_func_t = typing.Callable[[font_t, typing.Optional[builtins.object], builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
reference_table_func_t = typing.Callable[[face_t, builtins.int, typing.Optional[builtins.object]], blob_t]
unicode_combining_class_func_t = typing.Callable[[unicode_funcs_t, builtins.int, typing.Optional[builtins.object]], unicode_combining_class_t]
unicode_compose_func_t = typing.Callable[[unicode_funcs_t, builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
unicode_decompose_compatibility_func_t = typing.Callable[[unicode_funcs_t, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
unicode_decompose_func_t = typing.Callable[[unicode_funcs_t, builtins.int, builtins.int, builtins.int, typing.Optional[builtins.object]], builtins.int]
unicode_eastasian_width_func_t = typing.Callable[[unicode_funcs_t, builtins.int, typing.Optional[builtins.object]], builtins.int]
unicode_general_category_func_t = typing.Callable[[unicode_funcs_t, builtins.int, typing.Optional[builtins.object]], unicode_general_category_t]
unicode_mirroring_func_t = typing.Callable[[unicode_funcs_t, builtins.int, typing.Optional[builtins.object]], builtins.int]
unicode_script_func_t = typing.Callable[[unicode_funcs_t, builtins.int, typing.Optional[builtins.object]], script_t]


def blob_copy_writable_or_fail(blob: blob_t) -> blob_t: ...


def blob_create_from_file(file_name: builtins.str) -> blob_t: ...


def blob_create_sub_blob(parent: blob_t, offset: builtins.int, length: builtins.int) -> blob_t: ...


def blob_get_data(blob: blob_t) -> typing.Sequence[builtins.str]: ...


def blob_get_data_writable(blob: blob_t) -> typing.Sequence[builtins.str]: ...


def blob_get_empty() -> blob_t: ...


def blob_get_length(blob: blob_t) -> builtins.int: ...


def blob_is_immutable(blob: blob_t) -> builtins.int: ...


def blob_make_immutable(blob: blob_t) -> None: ...


def buffer_add(buffer: buffer_t, codepoint: builtins.int, cluster: builtins.int) -> None: ...


def buffer_add_codepoints(buffer: buffer_t, text: typing.Sequence[builtins.int], item_offset: builtins.int, item_length: builtins.int) -> None: ...


def buffer_add_latin1(buffer: buffer_t, text: builtins.bytes, item_offset: builtins.int, item_length: builtins.int) -> None: ...


def buffer_add_utf16(buffer: buffer_t, text: typing.Sequence[builtins.int], item_offset: builtins.int, item_length: builtins.int) -> None: ...


def buffer_add_utf32(buffer: buffer_t, text: typing.Sequence[builtins.int], item_offset: builtins.int, item_length: builtins.int) -> None: ...


def buffer_add_utf8(buffer: buffer_t, text: builtins.bytes, item_offset: builtins.int, item_length: builtins.int) -> None: ...


def buffer_allocation_successful(buffer: buffer_t) -> builtins.int: ...


def buffer_append(buffer: buffer_t, source: buffer_t, start: builtins.int, end: builtins.int) -> None: ...


def buffer_clear_contents(buffer: buffer_t) -> None: ...


def buffer_create() -> buffer_t: ...


def buffer_deserialize_glyphs(buffer: buffer_t, buf: typing.Sequence[builtins.str], font: font_t, format: buffer_serialize_format_t) -> typing.Tuple[builtins.int, builtins.str]: ...


def buffer_diff(buffer: buffer_t, reference: buffer_t, dottedcircle_glyph: builtins.int, position_fuzz: builtins.int) -> buffer_diff_flags_t: ...


def buffer_get_cluster_level(buffer: buffer_t) -> buffer_cluster_level_t: ...


def buffer_get_content_type(buffer: buffer_t) -> buffer_content_type_t: ...


def buffer_get_direction(buffer: buffer_t) -> direction_t: ...


def buffer_get_empty() -> buffer_t: ...


def buffer_get_flags(buffer: buffer_t) -> buffer_flags_t: ...


def buffer_get_glyph_infos(buffer: buffer_t) -> typing.Sequence[glyph_info_t]: ...


def buffer_get_glyph_positions(buffer: buffer_t) -> typing.Sequence[glyph_position_t]: ...


def buffer_get_invisible_glyph(buffer: buffer_t) -> builtins.int: ...


def buffer_get_language(buffer: buffer_t) -> language_t: ...


def buffer_get_length(buffer: buffer_t) -> builtins.int: ...


def buffer_get_replacement_codepoint(buffer: buffer_t) -> builtins.int: ...


def buffer_get_script(buffer: buffer_t) -> script_t: ...


def buffer_get_segment_properties(buffer: buffer_t) -> segment_properties_t: ...


def buffer_get_unicode_funcs(buffer: buffer_t) -> unicode_funcs_t: ...


def buffer_guess_segment_properties(buffer: buffer_t) -> None: ...


def buffer_normalize_glyphs(buffer: buffer_t) -> None: ...


def buffer_pre_allocate(buffer: buffer_t, size: builtins.int) -> builtins.int: ...


def buffer_reset(buffer: buffer_t) -> None: ...


def buffer_reverse(buffer: buffer_t) -> None: ...


def buffer_reverse_clusters(buffer: buffer_t) -> None: ...


def buffer_reverse_range(buffer: buffer_t, start: builtins.int, end: builtins.int) -> None: ...


def buffer_serialize_format_from_string(str: builtins.bytes) -> buffer_serialize_format_t: ...


def buffer_serialize_format_to_string(format: buffer_serialize_format_t) -> builtins.str: ...


def buffer_serialize_glyphs(buffer: buffer_t, start: builtins.int, end: builtins.int, font: typing.Optional[font_t], format: buffer_serialize_format_t, flags: buffer_serialize_flags_t) -> typing.Tuple[builtins.int, builtins.bytes, builtins.int]: ...


def buffer_serialize_list_formats() -> typing.Sequence[builtins.str]: ...


def buffer_set_cluster_level(buffer: buffer_t, cluster_level: buffer_cluster_level_t) -> None: ...


def buffer_set_content_type(buffer: buffer_t, content_type: buffer_content_type_t) -> None: ...


def buffer_set_direction(buffer: buffer_t, direction: direction_t) -> None: ...


def buffer_set_flags(buffer: buffer_t, flags: buffer_flags_t) -> None: ...


def buffer_set_invisible_glyph(buffer: buffer_t, invisible: builtins.int) -> None: ...


def buffer_set_language(buffer: buffer_t, language: language_t) -> None: ...


def buffer_set_length(buffer: buffer_t, length: builtins.int) -> builtins.int: ...


def buffer_set_message_func(buffer: buffer_t, func: buffer_message_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def buffer_set_replacement_codepoint(buffer: buffer_t, replacement: builtins.int) -> None: ...


def buffer_set_script(buffer: buffer_t, script: script_t) -> None: ...


def buffer_set_segment_properties(buffer: buffer_t, props: segment_properties_t) -> None: ...


def buffer_set_unicode_funcs(buffer: buffer_t, unicode_funcs: unicode_funcs_t) -> None: ...


def color_get_alpha(color: builtins.int) -> builtins.int: ...


def color_get_blue(color: builtins.int) -> builtins.int: ...


def color_get_green(color: builtins.int) -> builtins.int: ...


def color_get_red(color: builtins.int) -> builtins.int: ...


def direction_from_string(str: builtins.bytes) -> direction_t: ...


def direction_to_string(direction: direction_t) -> builtins.str: ...


def face_builder_add_table(face: face_t, tag: builtins.int, blob: blob_t) -> builtins.int: ...


def face_builder_create() -> face_t: ...


def face_collect_unicodes(face: face_t, out: set_t) -> None: ...


def face_collect_variation_selectors(face: face_t, out: set_t) -> None: ...


def face_collect_variation_unicodes(face: face_t, variation_selector: builtins.int, out: set_t) -> None: ...


def face_count(blob: blob_t) -> builtins.int: ...


def face_create(blob: blob_t, index: builtins.int) -> face_t: ...


def face_create_for_tables(reference_table_func: reference_table_func_t, *user_data: typing.Optional[builtins.object]) -> face_t: ...


def face_get_empty() -> face_t: ...


def face_get_glyph_count(face: face_t) -> builtins.int: ...


def face_get_index(face: face_t) -> builtins.int: ...


def face_get_table_tags(face: face_t, start_offset: builtins.int, table_count: builtins.int, table_tags: builtins.int) -> builtins.int: ...


def face_get_upem(face: face_t) -> builtins.int: ...


def face_is_immutable(face: face_t) -> builtins.int: ...


def face_make_immutable(face: face_t) -> None: ...


def face_reference_blob(face: face_t) -> blob_t: ...


def face_reference_table(face: face_t, tag: builtins.int) -> blob_t: ...


def face_set_glyph_count(face: face_t, glyph_count: builtins.int) -> None: ...


def face_set_index(face: face_t, index: builtins.int) -> None: ...


def face_set_upem(face: face_t, upem: builtins.int) -> None: ...


def feature_from_string(str: builtins.bytes) -> typing.Tuple[builtins.int, feature_t]: ...


def feature_to_string(feature: feature_t) -> typing.Sequence[builtins.str]: ...


def font_add_glyph_origin_for_direction(font: font_t, glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_create(face: face_t) -> font_t: ...


def font_create_sub_font(parent: font_t) -> font_t: ...


def font_funcs_create() -> font_funcs_t: ...


def font_funcs_get_empty() -> font_funcs_t: ...


def font_funcs_is_immutable(ffuncs: font_funcs_t) -> builtins.int: ...


def font_funcs_make_immutable(ffuncs: font_funcs_t) -> None: ...


def font_funcs_set_font_h_extents_func(ffuncs: font_funcs_t, func: font_get_font_extents_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_font_v_extents_func(ffuncs: font_funcs_t, func: font_get_font_extents_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_contour_point_func(ffuncs: font_funcs_t, func: font_get_glyph_contour_point_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_extents_func(ffuncs: font_funcs_t, func: font_get_glyph_extents_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_from_name_func(ffuncs: font_funcs_t, func: font_get_glyph_from_name_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_func(ffuncs: font_funcs_t, func: font_get_glyph_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_h_advance_func(ffuncs: font_funcs_t, func: font_get_glyph_advance_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_h_advances_func(ffuncs: font_funcs_t, func: font_get_glyph_advances_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_h_kerning_func(ffuncs: font_funcs_t, func: font_get_glyph_kerning_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_h_origin_func(ffuncs: font_funcs_t, func: font_get_glyph_origin_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_name_func(ffuncs: font_funcs_t, func: font_get_glyph_name_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_v_advance_func(ffuncs: font_funcs_t, func: font_get_glyph_advance_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_v_advances_func(ffuncs: font_funcs_t, func: font_get_glyph_advances_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_v_kerning_func(ffuncs: font_funcs_t, func: font_get_glyph_kerning_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_glyph_v_origin_func(ffuncs: font_funcs_t, func: font_get_glyph_origin_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_nominal_glyph_func(ffuncs: font_funcs_t, func: font_get_nominal_glyph_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_nominal_glyphs_func(ffuncs: font_funcs_t, func: font_get_nominal_glyphs_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_funcs_set_variation_glyph_func(ffuncs: font_funcs_t, func: font_get_variation_glyph_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def font_get_empty() -> font_t: ...


def font_get_extents_for_direction(font: font_t, direction: direction_t) -> font_extents_t: ...


def font_get_face(font: font_t) -> face_t: ...


def font_get_glyph(font: font_t, unicode: builtins.int, variation_selector: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_glyph_advance_for_direction(font: font_t, glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_glyph_advances_for_direction(font: font_t, direction: direction_t, count: builtins.int, first_glyph: builtins.int, glyph_stride: builtins.int, first_advance: builtins.int, advance_stride: builtins.int) -> None: ...


def font_get_glyph_contour_point(font: font_t, glyph: builtins.int, point_index: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def font_get_glyph_contour_point_for_origin(font: font_t, glyph: builtins.int, point_index: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def font_get_glyph_extents(font: font_t, glyph: builtins.int) -> typing.Tuple[builtins.int, glyph_extents_t]: ...


def font_get_glyph_extents_for_origin(font: font_t, glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, glyph_extents_t]: ...


def font_get_glyph_from_name(font: font_t, name: typing.Sequence[builtins.str]) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_glyph_h_advance(font: font_t, glyph: builtins.int) -> builtins.int: ...


def font_get_glyph_h_advances(font: font_t, count: builtins.int, first_glyph: builtins.int, glyph_stride: builtins.int, first_advance: builtins.int, advance_stride: builtins.int) -> None: ...


def font_get_glyph_h_kerning(font: font_t, left_glyph: builtins.int, right_glyph: builtins.int) -> builtins.int: ...


def font_get_glyph_h_origin(font: font_t, glyph: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def font_get_glyph_kerning_for_direction(font: font_t, first_glyph: builtins.int, second_glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_glyph_name(font: font_t, glyph: builtins.int, name: typing.Sequence[builtins.str]) -> builtins.int: ...


def font_get_glyph_origin_for_direction(font: font_t, glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_glyph_v_advance(font: font_t, glyph: builtins.int) -> builtins.int: ...


def font_get_glyph_v_advances(font: font_t, count: builtins.int, first_glyph: builtins.int, glyph_stride: builtins.int, first_advance: builtins.int, advance_stride: builtins.int) -> None: ...


def font_get_glyph_v_kerning(font: font_t, top_glyph: builtins.int, bottom_glyph: builtins.int) -> builtins.int: ...


def font_get_glyph_v_origin(font: font_t, glyph: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def font_get_h_extents(font: font_t) -> typing.Tuple[builtins.int, font_extents_t]: ...


def font_get_nominal_glyph(font: font_t, unicode: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_nominal_glyphs(font: font_t, count: builtins.int, first_unicode: builtins.int, unicode_stride: builtins.int, first_glyph: builtins.int, glyph_stride: builtins.int) -> builtins.int: ...


def font_get_parent(font: font_t) -> font_t: ...


def font_get_ppem(font: font_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_ptem(font: font_t) -> builtins.float: ...


def font_get_scale(font: font_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_get_v_extents(font: font_t) -> typing.Tuple[builtins.int, font_extents_t]: ...


def font_get_var_coords_normalized(font: font_t, length: builtins.int) -> builtins.int: ...


def font_get_variation_glyph(font: font_t, unicode: builtins.int, variation_selector: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_glyph_from_string(font: font_t, s: builtins.bytes) -> typing.Tuple[builtins.int, builtins.int]: ...


def font_glyph_to_string(font: font_t, glyph: builtins.int, s: typing.Sequence[builtins.str]) -> None: ...


def font_is_immutable(font: font_t) -> builtins.int: ...


def font_make_immutable(font: font_t) -> None: ...


def font_set_face(font: font_t, face: face_t) -> None: ...


def font_set_funcs(font: font_t, klass: font_funcs_t, font_data: typing.Optional[builtins.object], destroy: destroy_func_t) -> None: ...


def font_set_funcs_data(font: font_t, font_data: typing.Optional[builtins.object], destroy: destroy_func_t) -> None: ...


def font_set_parent(font: font_t, parent: font_t) -> None: ...


def font_set_ppem(font: font_t, x_ppem: builtins.int, y_ppem: builtins.int) -> None: ...


def font_set_ptem(font: font_t, ptem: builtins.float) -> None: ...


def font_set_scale(font: font_t, x_scale: builtins.int, y_scale: builtins.int) -> None: ...


def font_set_var_coords_design(font: font_t, coords: builtins.float, coords_length: builtins.int) -> None: ...


def font_set_var_coords_normalized(font: font_t, coords: builtins.int, coords_length: builtins.int) -> None: ...


def font_set_var_named_instance(font: font_t, instance_index: builtins.int) -> None: ...


def font_set_variations(font: font_t, variations: variation_t, variations_length: builtins.int) -> None: ...


def font_subtract_glyph_origin_for_direction(font: font_t, glyph: builtins.int, direction: direction_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def ft_font_changed(font: font_t) -> None: ...


def ft_font_get_load_flags(font: font_t) -> builtins.int: ...


def ft_font_set_funcs(font: font_t) -> None: ...


def ft_font_set_load_flags(font: font_t, load_flags: builtins.int) -> None: ...


def ft_font_unlock_face(font: font_t) -> None: ...


def glib_blob_create(gbytes: GLib.Bytes) -> blob_t: ...


def glib_get_unicode_funcs() -> unicode_funcs_t: ...


def glib_script_from_script(script: script_t) -> GLib.UnicodeScript: ...


def glib_script_to_script(script: GLib.UnicodeScript) -> script_t: ...


def glyph_info_get_glyph_flags(info: glyph_info_t) -> glyph_flags_t: ...


def language_from_string(str: builtins.bytes) -> language_t: ...


def language_get_default() -> language_t: ...


def language_to_string(language: language_t) -> builtins.str: ...


def map_allocation_successful(map: map_t) -> builtins.int: ...


def map_clear(map: map_t) -> None: ...


def map_create() -> map_t: ...


def map_del(map: map_t, key: builtins.int) -> None: ...


def map_get(map: map_t, key: builtins.int) -> builtins.int: ...


def map_get_empty() -> map_t: ...


def map_get_population(map: map_t) -> builtins.int: ...


def map_has(map: map_t, key: builtins.int) -> builtins.int: ...


def map_is_empty(map: map_t) -> builtins.int: ...


def map_set(map: map_t, key: builtins.int, value: builtins.int) -> None: ...


def ot_color_glyph_get_layers(face: face_t, glyph: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[ot_color_layer_t]]: ...


def ot_color_glyph_reference_png(font: font_t, glyph: builtins.int) -> blob_t: ...


def ot_color_glyph_reference_svg(face: face_t, glyph: builtins.int) -> blob_t: ...


def ot_color_has_layers(face: face_t) -> builtins.int: ...


def ot_color_has_palettes(face: face_t) -> builtins.int: ...


def ot_color_has_png(face: face_t) -> builtins.int: ...


def ot_color_has_svg(face: face_t) -> builtins.int: ...


def ot_color_palette_color_get_name_id(face: face_t, color_index: builtins.int) -> builtins.int: ...


def ot_color_palette_get_colors(face: face_t, palette_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_color_palette_get_count(face: face_t) -> builtins.int: ...


def ot_color_palette_get_flags(face: face_t, palette_index: builtins.int) -> ot_color_palette_flags_t: ...


def ot_color_palette_get_name_id(face: face_t, palette_index: builtins.int) -> builtins.int: ...


def ot_font_set_funcs(font: font_t) -> None: ...


def ot_layout_collect_features(face: face_t, table_tag: builtins.int, scripts: builtins.int, languages: builtins.int, features: builtins.int) -> set_t: ...


def ot_layout_collect_lookups(face: face_t, table_tag: builtins.int, scripts: builtins.int, languages: builtins.int, features: builtins.int) -> set_t: ...


def ot_layout_feature_get_characters(face: face_t, table_tag: builtins.int, feature_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_feature_get_lookups(face: face_t, table_tag: builtins.int, feature_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_feature_get_name_ids(face: face_t, table_tag: builtins.int, feature_index: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int, builtins.int, builtins.int, builtins.int]: ...


def ot_layout_feature_with_variations_get_lookups(face: face_t, table_tag: builtins.int, feature_index: builtins.int, variations_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_get_attach_points(face: face_t, glyph: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_get_baseline(font: font_t, baseline_tag: ot_layout_baseline_tag_t, direction: direction_t, script_tag: builtins.int, language_tag: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_get_glyph_class(face: face_t, glyph: builtins.int) -> ot_layout_glyph_class_t: ...


def ot_layout_get_glyphs_in_class(face: face_t, klass: ot_layout_glyph_class_t) -> set_t: ...


def ot_layout_get_ligature_carets(font: font_t, direction: direction_t, glyph: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_get_size_params(face: face_t) -> typing.Tuple[builtins.int, builtins.int, builtins.int, builtins.int, builtins.int, builtins.int]: ...


def ot_layout_has_glyph_classes(face: face_t) -> builtins.int: ...


def ot_layout_has_positioning(face: face_t) -> builtins.int: ...


def ot_layout_has_substitution(face: face_t) -> builtins.int: ...


def ot_layout_language_find_feature(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_index: builtins.int, feature_tag: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_language_get_feature_indexes(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_language_get_feature_tags(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_language_get_required_feature(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_index: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def ot_layout_language_get_required_feature_index(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_index: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_lookup_collect_glyphs(face: face_t, table_tag: builtins.int, lookup_index: builtins.int) -> typing.Tuple[set_t, set_t, set_t, set_t]: ...


def ot_layout_lookup_substitute_closure(face: face_t, lookup_index: builtins.int) -> set_t: ...


def ot_layout_lookup_would_substitute(face: face_t, lookup_index: builtins.int, glyphs: builtins.int, glyphs_length: builtins.int, zero_context: builtins.int) -> builtins.int: ...


def ot_layout_lookups_substitute_closure(face: face_t, lookups: set_t) -> set_t: ...


def ot_layout_script_find_language(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_tag: builtins.int, language_index: builtins.int) -> builtins.int: ...


def ot_layout_script_get_language_tags(face: face_t, table_tag: builtins.int, script_index: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_script_select_language(face: face_t, table_tag: builtins.int, script_index: builtins.int, language_count: builtins.int, language_tags: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_table_choose_script(face: face_t, table_tag: builtins.int, script_tags: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def ot_layout_table_find_feature_variations(face: face_t, table_tag: builtins.int, coords: builtins.int, num_coords: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_table_find_script(face: face_t, table_tag: builtins.int, script_tag: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_layout_table_get_feature_tags(face: face_t, table_tag: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_table_get_lookup_count(face: face_t, table_tag: builtins.int) -> builtins.int: ...


def ot_layout_table_get_script_tags(face: face_t, table_tag: builtins.int, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_layout_table_select_script(face: face_t, table_tag: builtins.int, script_count: builtins.int, script_tags: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def ot_math_get_constant(font: font_t, constant: ot_math_constant_t) -> builtins.int: ...


def ot_math_get_glyph_assembly(font: font_t, glyph: builtins.int, direction: direction_t, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[ot_math_glyph_part_t], builtins.int]: ...


def ot_math_get_glyph_italics_correction(font: font_t, glyph: builtins.int) -> builtins.int: ...


def ot_math_get_glyph_kerning(font: font_t, glyph: builtins.int, kern: ot_math_kern_t, correction_height: builtins.int) -> builtins.int: ...


def ot_math_get_glyph_top_accent_attachment(font: font_t, glyph: builtins.int) -> builtins.int: ...


def ot_math_get_glyph_variants(font: font_t, glyph: builtins.int, direction: direction_t, start_offset: builtins.int) -> typing.Tuple[builtins.int, typing.Sequence[ot_math_glyph_variant_t]]: ...


def ot_math_get_min_connector_overlap(font: font_t, direction: direction_t) -> builtins.int: ...


def ot_math_has_data(face: face_t) -> builtins.int: ...


def ot_math_is_glyph_extended_shape(face: face_t, glyph: builtins.int) -> builtins.int: ...


def ot_meta_get_entry_tags(face: face_t, start_offset: builtins.int, entries_count: builtins.int, entries: ot_meta_tag_t) -> builtins.int: ...


def ot_meta_reference_entry(face: face_t, meta_tag: ot_meta_tag_t) -> blob_t: ...


def ot_metrics_get_position(font: font_t, metrics_tag: ot_metrics_tag_t) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_metrics_get_variation(font: font_t, metrics_tag: ot_metrics_tag_t) -> builtins.float: ...


def ot_metrics_get_x_variation(font: font_t, metrics_tag: ot_metrics_tag_t) -> builtins.int: ...


def ot_metrics_get_y_variation(font: font_t, metrics_tag: ot_metrics_tag_t) -> builtins.int: ...


def ot_name_get_utf16(face: face_t, name_id: builtins.int, language: language_t) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_name_get_utf32(face: face_t, name_id: builtins.int, language: language_t) -> typing.Tuple[builtins.int, typing.Sequence[builtins.int]]: ...


def ot_name_get_utf8(face: face_t, name_id: builtins.int, language: language_t) -> typing.Tuple[builtins.int, typing.Sequence[builtins.str]]: ...


def ot_name_list_names(face: face_t) -> typing.Sequence[ot_name_entry_t]: ...


def ot_shape_glyphs_closure(font: font_t, buffer: buffer_t, features: feature_t, num_features: builtins.int, glyphs: set_t) -> None: ...


def ot_tag_from_language(language: language_t) -> builtins.int: ...


def ot_tag_to_language(tag: builtins.int) -> language_t: ...


def ot_tag_to_script(tag: builtins.int) -> script_t: ...


def ot_tags_from_script(script: script_t, script_tag_1: builtins.int, script_tag_2: builtins.int) -> None: ...


def ot_tags_from_script_and_language(script: script_t, language: language_t, script_count: typing.Optional[builtins.int], language_count: typing.Optional[builtins.int]) -> typing.Tuple[builtins.int, builtins.int]: ...


def ot_tags_to_script_and_language(script_tag: builtins.int, language_tag: builtins.int, script: typing.Optional[script_t], language: typing.Optional[language_t]) -> None: ...


def ot_var_find_axis(face: face_t, axis_tag: builtins.int, axis_index: builtins.int, axis_info: ot_var_axis_t) -> builtins.int: ...


def ot_var_find_axis_info(face: face_t, axis_tag: builtins.int, axis_info: ot_var_axis_info_t) -> builtins.int: ...


def ot_var_get_axes(face: face_t, start_offset: builtins.int, axes_count: builtins.int, axes_array: ot_var_axis_t) -> builtins.int: ...


def ot_var_get_axis_count(face: face_t) -> builtins.int: ...


def ot_var_get_axis_infos(face: face_t, start_offset: builtins.int, axes_count: builtins.int, axes_array: ot_var_axis_info_t) -> builtins.int: ...


def ot_var_get_named_instance_count(face: face_t) -> builtins.int: ...


def ot_var_has_data(face: face_t) -> builtins.int: ...


def ot_var_named_instance_get_design_coords(face: face_t, instance_index: builtins.int, coords_length: builtins.int, coords: builtins.float) -> builtins.int: ...


def ot_var_named_instance_get_postscript_name_id(face: face_t, instance_index: builtins.int) -> builtins.int: ...


def ot_var_named_instance_get_subfamily_name_id(face: face_t, instance_index: builtins.int) -> builtins.int: ...


def ot_var_normalize_coords(face: face_t, coords_length: builtins.int, design_coords: builtins.float, normalized_coords: builtins.int) -> None: ...


def ot_var_normalize_variations(face: face_t, variations: variation_t, variations_length: builtins.int, coords: builtins.int, coords_length: builtins.int) -> None: ...


def script_from_iso15924_tag(tag: builtins.int) -> script_t: ...


def script_from_string(str: builtins.bytes) -> script_t: ...


def script_get_horizontal_direction(script: script_t) -> direction_t: ...


def script_to_iso15924_tag(script: script_t) -> builtins.int: ...


def segment_properties_equal(a: segment_properties_t, b: segment_properties_t) -> builtins.int: ...


def segment_properties_hash(p: segment_properties_t) -> builtins.int: ...


def set_add(set: set_t, codepoint: builtins.int) -> None: ...


def set_add_range(set: set_t, first: builtins.int, last: builtins.int) -> None: ...


def set_allocation_successful(set: set_t) -> builtins.int: ...


def set_clear(set: set_t) -> None: ...


def set_create() -> set_t: ...


def set_del(set: set_t, codepoint: builtins.int) -> None: ...


def set_del_range(set: set_t, first: builtins.int, last: builtins.int) -> None: ...


def set_get_empty() -> set_t: ...


def set_get_max(set: set_t) -> builtins.int: ...


def set_get_min(set: set_t) -> builtins.int: ...


def set_get_population(set: set_t) -> builtins.int: ...


def set_has(set: set_t, codepoint: builtins.int) -> builtins.int: ...


def set_intersect(set: set_t, other: set_t) -> None: ...


def set_invert(set: set_t) -> None: ...


def set_is_empty(set: set_t) -> builtins.int: ...


def set_is_equal(set: set_t, other: set_t) -> builtins.int: ...


def set_is_subset(set: set_t, larger_set: set_t) -> builtins.int: ...


def set_next(set: set_t, codepoint: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def set_next_range(set: set_t, last: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def set_previous(set: set_t, codepoint: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def set_previous_range(set: set_t, first: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def set_set(set: set_t, other: set_t) -> None: ...


def set_subtract(set: set_t, other: set_t) -> None: ...


def set_symmetric_difference(set: set_t, other: set_t) -> None: ...


def set_union(set: set_t, other: set_t) -> None: ...


def shape(font: font_t, buffer: buffer_t, features: typing.Optional[typing.Sequence[feature_t]]) -> None: ...


def shape_full(font: font_t, buffer: buffer_t, features: typing.Optional[typing.Sequence[feature_t]], shaper_list: typing.Optional[typing.Sequence[builtins.str]]) -> builtins.int: ...


def shape_list_shapers() -> typing.Sequence[builtins.str]: ...


def shape_plan_create(face: face_t, props: segment_properties_t, user_features: typing.Sequence[feature_t], shaper_list: typing.Sequence[builtins.str]) -> shape_plan_t: ...


def shape_plan_create2(face: face_t, props: segment_properties_t, user_features: feature_t, num_user_features: builtins.int, coords: builtins.int, num_coords: builtins.int, shaper_list: builtins.str) -> shape_plan_t: ...


def shape_plan_create_cached(face: face_t, props: segment_properties_t, user_features: typing.Sequence[feature_t], shaper_list: typing.Sequence[builtins.str]) -> shape_plan_t: ...


def shape_plan_create_cached2(face: face_t, props: segment_properties_t, user_features: feature_t, num_user_features: builtins.int, coords: builtins.int, num_coords: builtins.int, shaper_list: builtins.str) -> shape_plan_t: ...


def shape_plan_execute(shape_plan: shape_plan_t, font: font_t, buffer: buffer_t, features: typing.Sequence[feature_t]) -> builtins.int: ...


def shape_plan_get_empty() -> shape_plan_t: ...


def shape_plan_get_shaper(shape_plan: shape_plan_t) -> builtins.str: ...


def tag_from_string(str: builtins.bytes) -> builtins.int: ...


def tag_to_string(tag: builtins.int) -> builtins.bytes: ...


def unicode_combining_class(ufuncs: unicode_funcs_t, unicode: builtins.int) -> unicode_combining_class_t: ...


def unicode_compose(ufuncs: unicode_funcs_t, a: builtins.int, b: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def unicode_decompose(ufuncs: unicode_funcs_t, ab: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def unicode_decompose_compatibility(ufuncs: unicode_funcs_t, u: builtins.int) -> typing.Tuple[builtins.int, builtins.int]: ...


def unicode_eastasian_width(ufuncs: unicode_funcs_t, unicode: builtins.int) -> builtins.int: ...


def unicode_funcs_create(parent: typing.Optional[unicode_funcs_t]) -> unicode_funcs_t: ...


def unicode_funcs_get_default() -> unicode_funcs_t: ...


def unicode_funcs_get_empty() -> unicode_funcs_t: ...


def unicode_funcs_get_parent(ufuncs: unicode_funcs_t) -> unicode_funcs_t: ...


def unicode_funcs_is_immutable(ufuncs: unicode_funcs_t) -> builtins.int: ...


def unicode_funcs_make_immutable(ufuncs: unicode_funcs_t) -> None: ...


def unicode_funcs_set_combining_class_func(ufuncs: unicode_funcs_t, func: unicode_combining_class_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_compose_func(ufuncs: unicode_funcs_t, func: unicode_compose_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_decompose_compatibility_func(ufuncs: unicode_funcs_t, func: unicode_decompose_compatibility_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_decompose_func(ufuncs: unicode_funcs_t, func: unicode_decompose_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_eastasian_width_func(ufuncs: unicode_funcs_t, func: unicode_eastasian_width_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_general_category_func(ufuncs: unicode_funcs_t, func: unicode_general_category_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_mirroring_func(ufuncs: unicode_funcs_t, func: unicode_mirroring_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_funcs_set_script_func(ufuncs: unicode_funcs_t, func: unicode_script_func_t, *user_data: typing.Optional[builtins.object]) -> None: ...


def unicode_general_category(ufuncs: unicode_funcs_t, unicode: builtins.int) -> unicode_general_category_t: ...


def unicode_mirroring(ufuncs: unicode_funcs_t, unicode: builtins.int) -> builtins.int: ...


def unicode_script(ufuncs: unicode_funcs_t, unicode: builtins.int) -> script_t: ...


def variation_from_string(str: builtins.str, len: builtins.int, variation: variation_t) -> builtins.int: ...


def variation_to_string(variation: variation_t, buf: builtins.str, size: builtins.int) -> None: ...


def version() -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def version_atleast(major: builtins.int, minor: builtins.int, micro: builtins.int) -> builtins.int: ...


def version_string() -> builtins.str: ...


AAT_LAYOUT_NO_SELECTOR_INDEX: builtins.int
BUFFER_REPLACEMENT_CODEPOINT_DEFAULT: builtins.int
FEATURE_GLOBAL_START: builtins.int
MAP_VALUE_INVALID: builtins.int
OT_LAYOUT_DEFAULT_LANGUAGE_INDEX: builtins.int
OT_LAYOUT_NO_FEATURE_INDEX: builtins.int
OT_LAYOUT_NO_SCRIPT_INDEX: builtins.int
OT_LAYOUT_NO_VARIATIONS_INDEX: builtins.int
OT_MAX_TAGS_PER_LANGUAGE: builtins.int
OT_MAX_TAGS_PER_SCRIPT: builtins.int
OT_VAR_NO_AXIS_INDEX: builtins.int
SET_VALUE_INVALID: builtins.int
UNICODE_MAX: builtins.int
UNICODE_MAX_DECOMPOSITION_LEN: builtins.int
VERSION_MAJOR: builtins.int
VERSION_MICRO: builtins.int
VERSION_MINOR: builtins.int
VERSION_STRING: builtins.str
