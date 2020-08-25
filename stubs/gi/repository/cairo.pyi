import builtins
import typing

from gi.repository import GObject


class Context():
    ...


class Device():
    ...


class FontFace():
    ...


class FontOptions():
    ...


class Matrix():
    ...


class Path():
    ...


class Pattern():
    ...


class Rectangle():
    height: builtins.float
    width: builtins.float
    x: builtins.float
    y: builtins.float


class RectangleInt():
    height: builtins.int
    width: builtins.int
    x: builtins.int
    y: builtins.int


class Region():
    ...


class ScaledFont():
    ...


class Surface():
    ...


class Antialias(GObject.GEnum, builtins.int):
    BEST = ...  # type: Antialias
    DEFAULT = ...  # type: Antialias
    FAST = ...  # type: Antialias
    GOOD = ...  # type: Antialias
    GRAY = ...  # type: Antialias
    NONE = ...  # type: Antialias
    SUBPIXEL = ...  # type: Antialias


class Content(GObject.GEnum, builtins.int):
    ALPHA = ...  # type: Content
    COLOR = ...  # type: Content
    COLOR_ALPHA = ...  # type: Content


class DeviceType(GObject.GEnum, builtins.int):
    COGL = ...  # type: DeviceType
    DRM = ...  # type: DeviceType
    GL = ...  # type: DeviceType
    INVALID = ...  # type: DeviceType
    SCRIPT = ...  # type: DeviceType
    WIN32 = ...  # type: DeviceType
    XCB = ...  # type: DeviceType
    XLIB = ...  # type: DeviceType
    XML = ...  # type: DeviceType


class Extend(GObject.GEnum, builtins.int):
    NONE = ...  # type: Extend
    PAD = ...  # type: Extend
    REFLECT = ...  # type: Extend
    REPEAT = ...  # type: Extend


class FillRule(GObject.GEnum, builtins.int):
    EVEN_ODD = ...  # type: FillRule
    WINDING = ...  # type: FillRule


class Filter(GObject.GEnum, builtins.int):
    BEST = ...  # type: Filter
    BILINEAR = ...  # type: Filter
    FAST = ...  # type: Filter
    GAUSSIAN = ...  # type: Filter
    GOOD = ...  # type: Filter
    NEAREST = ...  # type: Filter


class FontSlant(GObject.GEnum, builtins.int):
    ITALIC = ...  # type: FontSlant
    NORMAL = ...  # type: FontSlant
    OBLIQUE = ...  # type: FontSlant


class FontType(GObject.GEnum, builtins.int):
    FT = ...  # type: FontType
    QUARTZ = ...  # type: FontType
    TOY = ...  # type: FontType
    USER = ...  # type: FontType
    WIN32 = ...  # type: FontType


class FontWeight(GObject.GEnum, builtins.int):
    BOLD = ...  # type: FontWeight
    NORMAL = ...  # type: FontWeight


class Format(GObject.GEnum, builtins.int):
    A1 = ...  # type: Format
    A8 = ...  # type: Format
    ARGB32 = ...  # type: Format
    INVALID = ...  # type: Format
    RGB16_565 = ...  # type: Format
    RGB24 = ...  # type: Format
    RGB30 = ...  # type: Format


class HintMetrics(GObject.GEnum, builtins.int):
    DEFAULT = ...  # type: HintMetrics
    OFF = ...  # type: HintMetrics
    ON = ...  # type: HintMetrics


class HintStyle(GObject.GEnum, builtins.int):
    DEFAULT = ...  # type: HintStyle
    FULL = ...  # type: HintStyle
    MEDIUM = ...  # type: HintStyle
    NONE = ...  # type: HintStyle
    SLIGHT = ...  # type: HintStyle


class LineCap(GObject.GEnum, builtins.int):
    BUTT = ...  # type: LineCap
    ROUND = ...  # type: LineCap
    SQUARE = ...  # type: LineCap


class LineJoin(GObject.GEnum, builtins.int):
    BEVEL = ...  # type: LineJoin
    MITER = ...  # type: LineJoin
    ROUND = ...  # type: LineJoin


class Operator(GObject.GEnum, builtins.int):
    ADD = ...  # type: Operator
    ATOP = ...  # type: Operator
    CLEAR = ...  # type: Operator
    COLOR_BURN = ...  # type: Operator
    COLOR_DODGE = ...  # type: Operator
    DARKEN = ...  # type: Operator
    DEST = ...  # type: Operator
    DEST_ATOP = ...  # type: Operator
    DEST_IN = ...  # type: Operator
    DEST_OUT = ...  # type: Operator
    DEST_OVER = ...  # type: Operator
    DIFFERENCE = ...  # type: Operator
    EXCLUSION = ...  # type: Operator
    HARD_LIGHT = ...  # type: Operator
    HSL_COLOR = ...  # type: Operator
    HSL_HUE = ...  # type: Operator
    HSL_LUMINOSITY = ...  # type: Operator
    HSL_SATURATION = ...  # type: Operator
    IN = ...  # type: Operator
    LIGHTEN = ...  # type: Operator
    MULTIPLY = ...  # type: Operator
    OUT = ...  # type: Operator
    OVER = ...  # type: Operator
    OVERLAY = ...  # type: Operator
    SATURATE = ...  # type: Operator
    SCREEN = ...  # type: Operator
    SOFT_LIGHT = ...  # type: Operator
    SOURCE = ...  # type: Operator
    XOR = ...  # type: Operator


class PathDataType(GObject.GEnum, builtins.int):
    CLOSE_PATH = ...  # type: PathDataType
    CURVE_TO = ...  # type: PathDataType
    LINE_TO = ...  # type: PathDataType
    MOVE_TO = ...  # type: PathDataType


class PatternType(GObject.GEnum, builtins.int):
    LINEAR = ...  # type: PatternType
    MESH = ...  # type: PatternType
    RADIAL = ...  # type: PatternType
    RASTER_SOURCE = ...  # type: PatternType
    SOLID = ...  # type: PatternType
    SURFACE = ...  # type: PatternType


class RegionOverlap(GObject.GEnum, builtins.int):
    IN = ...  # type: RegionOverlap
    OUT = ...  # type: RegionOverlap
    PART = ...  # type: RegionOverlap


class Status(GObject.GEnum, builtins.int):
    CLIP_NOT_REPRESENTABLE = ...  # type: Status
    DEVICE_ERROR = ...  # type: Status
    DEVICE_FINISHED = ...  # type: Status
    DEVICE_TYPE_MISMATCH = ...  # type: Status
    FILE_NOT_FOUND = ...  # type: Status
    FONT_TYPE_MISMATCH = ...  # type: Status
    INVALID_CLUSTERS = ...  # type: Status
    INVALID_CONTENT = ...  # type: Status
    INVALID_DASH = ...  # type: Status
    INVALID_DSC_COMMENT = ...  # type: Status
    INVALID_FORMAT = ...  # type: Status
    INVALID_INDEX = ...  # type: Status
    INVALID_MATRIX = ...  # type: Status
    INVALID_MESH_CONSTRUCTION = ...  # type: Status
    INVALID_PATH_DATA = ...  # type: Status
    INVALID_POP_GROUP = ...  # type: Status
    INVALID_RESTORE = ...  # type: Status
    INVALID_SIZE = ...  # type: Status
    INVALID_SLANT = ...  # type: Status
    INVALID_STATUS = ...  # type: Status
    INVALID_STRIDE = ...  # type: Status
    INVALID_STRING = ...  # type: Status
    INVALID_VISUAL = ...  # type: Status
    INVALID_WEIGHT = ...  # type: Status
    JBIG2_GLOBAL_MISSING = ...  # type: Status
    NEGATIVE_COUNT = ...  # type: Status
    NO_CURRENT_POINT = ...  # type: Status
    NO_MEMORY = ...  # type: Status
    NULL_POINTER = ...  # type: Status
    PATTERN_TYPE_MISMATCH = ...  # type: Status
    READ_ERROR = ...  # type: Status
    SUCCESS = ...  # type: Status
    SURFACE_FINISHED = ...  # type: Status
    SURFACE_TYPE_MISMATCH = ...  # type: Status
    TEMP_FILE_ERROR = ...  # type: Status
    USER_FONT_ERROR = ...  # type: Status
    USER_FONT_IMMUTABLE = ...  # type: Status
    USER_FONT_NOT_IMPLEMENTED = ...  # type: Status
    WRITE_ERROR = ...  # type: Status


class SubpixelOrder(GObject.GEnum, builtins.int):
    BGR = ...  # type: SubpixelOrder
    DEFAULT = ...  # type: SubpixelOrder
    RGB = ...  # type: SubpixelOrder
    VBGR = ...  # type: SubpixelOrder
    VRGB = ...  # type: SubpixelOrder


class SurfaceType(GObject.GEnum, builtins.int):
    BEOS = ...  # type: SurfaceType
    COGL = ...  # type: SurfaceType
    DIRECTFB = ...  # type: SurfaceType
    DRM = ...  # type: SurfaceType
    GL = ...  # type: SurfaceType
    GLITZ = ...  # type: SurfaceType
    IMAGE = ...  # type: SurfaceType
    OS2 = ...  # type: SurfaceType
    PDF = ...  # type: SurfaceType
    PS = ...  # type: SurfaceType
    QT = ...  # type: SurfaceType
    QUARTZ = ...  # type: SurfaceType
    QUARTZ_IMAGE = ...  # type: SurfaceType
    RECORDING = ...  # type: SurfaceType
    SCRIPT = ...  # type: SurfaceType
    SKIA = ...  # type: SurfaceType
    SUBSURFACE = ...  # type: SurfaceType
    SVG = ...  # type: SurfaceType
    TEE = ...  # type: SurfaceType
    VG = ...  # type: SurfaceType
    WIN32 = ...  # type: SurfaceType
    WIN32_PRINTING = ...  # type: SurfaceType
    XCB = ...  # type: SurfaceType
    XLIB = ...  # type: SurfaceType
    XML = ...  # type: SurfaceType


class TextClusterFlags(GObject.GEnum, builtins.int):
    BACKWARD = ...  # type: TextClusterFlags


def image_surface_create() -> None: ...


