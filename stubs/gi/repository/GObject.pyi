import builtins
import typing

from gi.repository import GLib


# TODO: Constrain T if possible. Builtins + GTypes might be sufficient?
T = typing.TypeVar('T')

PropertyGetterFn = typing.Callable[[typing.Any], T]
PropertySetterFn = typing.Callable[[typing.Any, T], None]


class Property(typing.Generic[T]):

    name: typing.Optional[str]
    type: typing.Type[T]
    default: typing.Optional[T]
    nick: str
    blurb: str
    flags: ParamFlags
    minimum: typing.Optional[T]
    maximum: typing.Optional[T]

    def __init__(
        self,
        getter: typing.Optional[PropertyGetterFn[T]] = None,
        setter: typing.Optional[PropertySetterFn[T]] = None,
        type: typing.Optional[typing.Type[T]] = None,
        default: typing.Optional[T] = None,
        nick: str = '',
        blurb: str = '',
        flags: ParamFlags = ParamFlags.READWRITE,
        minimum: typing.Optional[T] = None,
        maximum: typing.Optional[T] = None,
    ) -> None:
        ...

    def __get__(self, instance: typing.Any, klass: typing.Type[T]) -> T:
        ...

    def __set__(self, instance: typing.Any, value: T) -> None:
        ...

    def __call__(self, fget: PropertyGetterFn[T]) -> Property[T]:
        ...

    def getter(self: Property[T], fget: PropertyGetterFn[T]) -> Property[T]:
        ...

    def setter(self: Property[T], fset: PropertySetterFn[T]) -> Property[T]:
        ...

    # TODO: There's three Tuple variant structures that could be
    # returned here, and they're all unpleasantly complicated.
    def get_pspec_args(self) -> typing.Sequence[typing.Any]:
        ...


class GType():
    pass

class GInterface():
    ...


class Object():
    Property = Property
    g_type_instance: TypeInstance
    qdata: GLib.Data
    ref_count: builtins.int

    def bind_property(self, source_property: builtins.str, target: Object, target_property: builtins.str, flags: BindingFlags) -> Binding: ...

    def bind_property_full(self, source_property: builtins.str, target: Object, target_property: builtins.str, flags: BindingFlags, transform_to: Closure, transform_from: Closure) -> Binding: ...

    @staticmethod
    def compat_control(what: builtins.int, data: typing.Optional[builtins.object]) -> builtins.int: ...

    T = typing.TypeVar("T")
    T1 = typing.TypeVar("T1")
    T2 = typing.TypeVar("T2")
    T3 = typing.TypeVar("T3")

    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, typing.Any, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, typing.Any, typing.Any, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, typing.Any, typing.Any, typing.Any, typing.Any], typing.Any]) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, T1], typing.Any], user_data1: T1) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, T1], typing.Any], user_data1: T1) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, T1], typing.Any], user_data1: T1) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, typing.Any, typing.Any, T1], typing.Any], user_data1: T1) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, T1, T2], typing.Any], user_data1: T1, user_data2: T2) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, typing.Any, T1, T2], typing.Any], user_data1: T1, user_data2: T2) -> int: ...
    @typing.overload
    def connect(self: T, detailed_signal: str, handler: typing.Callable[[T, T1, T2, T3], typing.Any], user_data1: T1, user_data2: T2, user_data3: T3) -> int: ...

    def connect_after(self, detailed_signal: builtins.str, handler: function, *args: typing.Any) -> builtins.int: ...

    def disconnect(self, handler_id: int) -> None: ...

    def emit(self, signal_name: builtins.str, *args: typing.Any) -> None: ...

    def force_floating(self) -> None: ...

    def freeze_notify(self) -> None: ...

    def get_data(self, key: builtins.str) -> typing.Optional[builtins.object]: ...

    def get_property(self, property_name: builtins.str) -> builtins.object: ...

    def get_qdata(self, quark: builtins.int) -> typing.Optional[builtins.object]: ...

    def getv(self, names: typing.Sequence[builtins.str], values: typing.Sequence[Value]) -> None: ...

    def handler_block(self, handler_id: builtins.int) -> None: ...

    def handler_is_connected(self, handler_id: int) -> bool: ...

    def handler_unblock(self, handler_id: builtins.int) -> None: ...

    @staticmethod
    def interface_find_property(g_iface: TypeInterface, property_name: builtins.str) -> ParamSpec: ...

    @staticmethod
    def interface_install_property(g_iface: TypeInterface, pspec: ParamSpec) -> None: ...

    @staticmethod
    def interface_list_properties(g_iface: TypeInterface) -> typing.Sequence[ParamSpec]: ...

    def is_floating(self) -> builtins.bool: ...

    def notify(self, property_name: builtins.str) -> None: ...

    def notify_by_pspec(self, pspec: ParamSpec) -> None: ...

    def ref(self) -> Object: ...

    def ref_sink(self) -> Object: ...

    def run_dispose(self) -> None: ...

    def set_data(self, key: builtins.str, data: typing.Optional[builtins.object]) -> None: ...

    def set_property(self, property_name: builtins.str, value: builtins.object) -> None: ...

    def set_properties(self, **properties: object) -> None: ...

    def steal_data(self, key: builtins.str) -> typing.Optional[builtins.object]: ...

    def steal_qdata(self, quark: builtins.int) -> typing.Optional[builtins.object]: ...

    def stop_emission(self, detailed_signal: str) -> None: ...

    def thaw_notify(self) -> None: ...

    def unref(self) -> None: ...

    def watch_closure(self, closure: Closure) -> None: ...

    @staticmethod
    def find_property(property_name: builtins.str) -> ParamSpec: ...

    @staticmethod
    def install_properties(pspecs: typing.Sequence[ParamSpec]) -> None: ...

    @staticmethod
    def install_property(property_id: builtins.int, pspec: ParamSpec) -> None: ...

    @staticmethod
    def list_properties() -> typing.Sequence[ParamSpec]: ...

    @staticmethod
    def override_property(property_id: builtins.int, name: builtins.str) -> None: ...

    def do_constructed(self) -> None: ...

    def do_dispatch_properties_changed(self, n_pspecs: builtins.int, pspecs: ParamSpec) -> None: ...

    def do_dispose(self) -> None: ...

    def do_finalize(self) -> None: ...

    def do_get_property(self, property_id: builtins.int, value: Value, pspec: ParamSpec) -> None: ...

    def do_notify(self, pspec: ParamSpec) -> None: ...

    def do_set_property(self, property_id: builtins.int, value: Value, pspec: ParamSpec) -> None: ...


class ParamSpec():
    flags: ParamFlags
    g_type_instance: TypeInstance
    name: builtins.str
    owner_type: GType
    param_id: builtins.int
    qdata: GLib.Data
    ref_count: builtins.int
    value_type: GType

    def get_blurb(self) -> builtins.str: ...

    def get_default_value(self) -> Value: ...

    def get_name(self) -> builtins.str: ...

    def get_name_quark(self) -> builtins.int: ...

    def get_nick(self) -> builtins.str: ...

    def get_qdata(self, quark: builtins.int) -> typing.Optional[builtins.object]: ...

    def get_redirect_target(self) -> ParamSpec: ...

    def set_qdata(self, quark: builtins.int, data: typing.Optional[builtins.object]) -> None: ...

    def sink(self) -> None: ...

    def steal_qdata(self, quark: builtins.int) -> typing.Optional[builtins.object]: ...

    def do_finalize(self) -> None: ...

    def do_value_set_default(self, value: Value) -> None: ...

    def do_value_validate(self, value: Value) -> builtins.bool: ...

    def do_values_cmp(self, value1: Value, value2: Value) -> builtins.int: ...


class TypePlugin(GInterface):

    def complete_interface_info(self, instance_type: GType, interface_type: GType, info: InterfaceInfo) -> None: ...

    def complete_type_info(self, g_type: GType, info: TypeInfo, value_table: TypeValueTable) -> None: ...

    def unuse(self) -> None: ...

    def use(self) -> None: ...


class Binding(Object):

    def get_flags(self) -> BindingFlags: ...

    def get_source(self) -> Object: ...

    def get_source_property(self) -> builtins.str: ...

    def get_target(self) -> Object: ...

    def get_target_property(self) -> builtins.str: ...

    def unbind(self) -> None: ...


class InitiallyUnowned(Object):
    g_type_instance: TypeInstance
    qdata: GLib.Data
    ref_count: builtins.int


class ParamSpecBoolean(ParamSpec):
    default_value: builtins.bool
    parent_instance: ParamSpec


class ParamSpecBoxed(ParamSpec):
    parent_instance: ParamSpec


class ParamSpecChar(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecDouble(ParamSpec):
    default_value: builtins.float
    epsilon: builtins.float
    maximum: builtins.float
    minimum: builtins.float
    parent_instance: ParamSpec


class ParamSpecEnum(ParamSpec):
    default_value: builtins.int
    enum_class: EnumClass
    parent_instance: ParamSpec


class ParamSpecFlags(ParamSpec):
    default_value: builtins.int
    flags_class: FlagsClass
    parent_instance: ParamSpec


class ParamSpecFloat(ParamSpec):
    default_value: builtins.float
    epsilon: builtins.float
    maximum: builtins.float
    minimum: builtins.float
    parent_instance: ParamSpec


class ParamSpecGType(ParamSpec):
    is_a_type: GType
    parent_instance: ParamSpec


class ParamSpecInt(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecInt64(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecLong(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecObject(ParamSpec):
    parent_instance: ParamSpec


class ParamSpecOverride(ParamSpec):
    overridden: ParamSpec
    parent_instance: ParamSpec


class ParamSpecParam(ParamSpec):
    parent_instance: ParamSpec


class ParamSpecPointer(ParamSpec):
    parent_instance: ParamSpec


class ParamSpecString(ParamSpec):
    cset_first: builtins.str
    cset_nth: builtins.str
    default_value: builtins.str
    ensure_non_null: builtins.int
    null_fold_if_empty: builtins.int
    parent_instance: ParamSpec
    substitutor: builtins.int


class ParamSpecUChar(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecUInt(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecUInt64(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecULong(ParamSpec):
    default_value: builtins.int
    maximum: builtins.int
    minimum: builtins.int
    parent_instance: ParamSpec


class ParamSpecUnichar(ParamSpec):
    default_value: builtins.str
    parent_instance: ParamSpec


class ParamSpecValueArray(ParamSpec):
    element_spec: ParamSpec
    fixed_n_elements: builtins.int
    parent_instance: ParamSpec


class ParamSpecVariant(ParamSpec):
    default_value: GLib.Variant
    padding: typing.Sequence[builtins.object]
    parent_instance: ParamSpec
    type: GLib.VariantType


class TypeModule(Object, TypePlugin):
    interface_infos: typing.Sequence[builtins.object]
    name: builtins.str
    parent_instance: Object
    type_infos: typing.Sequence[builtins.object]
    use_count: builtins.int

    def add_interface(self, instance_type: GType, interface_type: GType, interface_info: InterfaceInfo) -> None: ...

    def register_enum(self, name: builtins.str, const_static_values: EnumValue) -> GType: ...

    def register_flags(self, name: builtins.str, const_static_values: FlagsValue) -> GType: ...

    def register_type(self, parent_type: GType, type_name: builtins.str, type_info: TypeInfo, flags: TypeFlags) -> GType: ...

    def set_name(self, name: builtins.str) -> None: ...

    def unuse(self) -> None: ...

    def use(self) -> builtins.bool: ...  # type: ignore

    def do_load(self) -> builtins.bool: ...

    def do_unload(self) -> None: ...


class CClosure():
    callback: builtins.object
    closure: Closure

    @staticmethod
    def marshal_BOOLEAN__BOXED_BOXED(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_BOOLEAN__FLAGS(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_STRING__OBJECT_POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__BOOLEAN(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__BOXED(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__CHAR(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__DOUBLE(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__ENUM(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__FLAGS(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__FLOAT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__INT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__LONG(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__OBJECT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__PARAM(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__STRING(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__UCHAR(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__UINT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__UINT_POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__ULONG(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__VARIANT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_VOID__VOID(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def marshal_generic(closure: Closure, return_gvalue: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


class Closure():
    data: builtins.object
    derivative_flag: builtins.int
    floating: builtins.int
    in_inotify: builtins.int
    in_marshal: builtins.int
    is_invalid: builtins.int
    marshal: builtins.object
    meta_marshal_nouse: builtins.int
    n_fnotifiers: builtins.int
    n_guards: builtins.int
    n_inotifiers: builtins.int
    notifiers: ClosureNotifyData
    ref_count: builtins.int

    def invalidate(self) -> None: ...

    def invoke(self, param_values: typing.Sequence[Value], invocation_hint: typing.Optional[builtins.object]) -> Value: ...

    @staticmethod
    def new_object(sizeof_closure: builtins.int, object: Object) -> Closure: ...

    @staticmethod
    def new_simple(sizeof_closure: builtins.int, data: typing.Optional[builtins.object]) -> Closure: ...

    def ref(self) -> Closure: ...

    def sink(self) -> None: ...

    def unref(self) -> None: ...


class ClosureNotifyData():
    data: builtins.object
    notify: ClosureNotify


class EnumClass():
    g_type_class: TypeClass
    maximum: builtins.int
    minimum: builtins.int
    n_values: builtins.int
    values: EnumValue


class EnumValue():
    value: builtins.int
    value_name: builtins.str
    value_nick: builtins.str


class FlagsClass():
    g_type_class: TypeClass
    mask: builtins.int
    n_values: builtins.int
    values: FlagsValue


class FlagsValue():
    value: builtins.int
    value_name: builtins.str
    value_nick: builtins.str


class InterfaceInfo():
    interface_data: builtins.object
    interface_finalize: InterfaceFinalizeFunc
    interface_init: InterfaceInitFunc


class ObjectConstructParam():
    pspec: ParamSpec
    value: Value


class ParamSpecPool():

    def insert(self, pspec: ParamSpec, owner_type: GType) -> None: ...

    def list(self, owner_type: GType) -> typing.Sequence[ParamSpec]: ...

    def list_owned(self, owner_type: GType) -> typing.Sequence[ParamSpec]: ...

    def lookup(self, param_name: builtins.str, owner_type: GType, walk_ancestors: builtins.bool) -> ParamSpec: ...

    @staticmethod
    def new(type_prefixing: builtins.bool) -> ParamSpecPool: ...

    def remove(self, pspec: ParamSpec) -> None: ...


class ParamSpecTypeInfo():
    finalize: builtins.object
    instance_init: builtins.object
    instance_size: builtins.int
    n_preallocs: builtins.int
    value_set_default: builtins.object
    value_type: GType
    value_validate: builtins.object
    values_cmp: builtins.object


class Parameter():
    name: builtins.str
    value: Value


class SignalInvocationHint():
    detail: builtins.int
    run_type: SignalFlags
    signal_id: builtins.int


class SignalQuery():
    itype: GType
    n_params: builtins.int
    param_types: typing.Sequence[GType]
    return_type: GType
    signal_flags: SignalFlags
    signal_id: builtins.int
    signal_name: builtins.str


class TypeClass():
    g_type: GType

    def add_private(self, private_size: builtins.int) -> None: ...

    @staticmethod
    def adjust_private_offset(g_class: typing.Optional[builtins.object], private_size_or_offset: builtins.int) -> None: ...

    def get_private(self, private_type: GType) -> typing.Optional[builtins.object]: ...

    @staticmethod
    def peek(type: GType) -> TypeClass: ...

    def peek_parent(self) -> TypeClass: ...

    @staticmethod
    def peek_static(type: GType) -> TypeClass: ...

    @staticmethod
    def ref(type: GType) -> TypeClass: ...

    def unref(self) -> None: ...


class TypeFundamentalInfo():
    type_flags: TypeFundamentalFlags


class TypeInfo():
    base_finalize: BaseFinalizeFunc
    base_init: BaseInitFunc
    class_data: builtins.object
    class_finalize: ClassFinalizeFunc
    class_init: ClassInitFunc
    class_size: builtins.int
    instance_init: InstanceInitFunc
    instance_size: builtins.int
    n_preallocs: builtins.int
    value_table: TypeValueTable


class TypeInstance():
    g_class: TypeClass

    def get_private(self, private_type: GType) -> typing.Optional[builtins.object]: ...


class TypeInterface():
    g_instance_type: GType
    g_type: GType

    @staticmethod
    def add_prerequisite(interface_type: GType, prerequisite_type: GType) -> None: ...

    @staticmethod
    def get_plugin(instance_type: GType, interface_type: GType) -> TypePlugin: ...

    @staticmethod
    def peek(instance_class: TypeClass, iface_type: GType) -> TypeInterface: ...

    def peek_parent(self) -> TypeInterface: ...

    @staticmethod
    def prerequisites(interface_type: GType) -> typing.Sequence[GType]: ...


class TypePluginClass():
    base_iface: TypeInterface
    complete_interface_info: TypePluginCompleteInterfaceInfo
    complete_type_info: TypePluginCompleteTypeInfo
    unuse_plugin: TypePluginUnuse
    use_plugin: TypePluginUse


class TypeQuery():
    class_size: builtins.int
    instance_size: builtins.int
    type: GType
    type_name: builtins.str


class TypeValueTable():
    collect_format: builtins.str
    collect_value: builtins.object
    lcopy_format: builtins.str
    lcopy_value: builtins.object
    value_copy: builtins.object
    value_free: builtins.object
    value_init: builtins.object
    value_peek_pointer: builtins.object


class Value():
    g_type: GType

    def copy(self, dest_value: Value) -> None: ...

    def dup_object(self) -> Object: ...

    def dup_string(self) -> builtins.str: ...

    def dup_variant(self) -> typing.Optional[GLib.Variant]: ...

    def fits_pointer(self) -> builtins.bool: ...

    def get_boolean(self) -> builtins.bool: ...

    def get_boxed(self) -> typing.Optional[builtins.object]: ...

    def get_char(self) -> builtins.int: ...

    def get_double(self) -> builtins.float: ...

    def get_enum(self) -> builtins.int: ...

    def get_flags(self) -> builtins.int: ...

    def get_float(self) -> builtins.float: ...

    def get_gtype(self) -> GType: ...

    def get_int(self) -> builtins.int: ...

    def get_int64(self) -> builtins.int: ...

    def get_long(self) -> builtins.int: ...

    def get_object(self) -> Object: ...

    def get_param(self) -> ParamSpec: ...

    def get_pointer(self) -> typing.Optional[builtins.object]: ...

    def get_schar(self) -> builtins.int: ...

    def get_string(self) -> builtins.str: ...

    def get_uchar(self) -> builtins.int: ...

    def get_uint(self) -> builtins.int: ...

    def get_uint64(self) -> builtins.int: ...

    def get_ulong(self) -> builtins.int: ...

    def get_variant(self) -> typing.Optional[GLib.Variant]: ...

    def init(self, g_type: GType) -> Value: ...

    def init_from_instance(self, instance: TypeInstance) -> None: ...

    def peek_pointer(self) -> typing.Optional[builtins.object]: ...

    def reset(self) -> Value: ...

    def set_boolean(self, v_boolean: builtins.bool) -> None: ...

    def set_boxed(self, v_boxed: typing.Optional[builtins.object]) -> None: ...

    def set_boxed_take_ownership(self, v_boxed: typing.Optional[builtins.object]) -> None: ...

    def set_char(self, v_char: builtins.int) -> None: ...

    def set_double(self, v_double: builtins.float) -> None: ...

    def set_enum(self, v_enum: builtins.int) -> None: ...

    def set_flags(self, v_flags: builtins.int) -> None: ...

    def set_float(self, v_float: builtins.float) -> None: ...

    def set_gtype(self, v_gtype: GType) -> None: ...

    def set_instance(self, instance: typing.Optional[builtins.object]) -> None: ...

    def set_int(self, v_int: builtins.int) -> None: ...

    def set_int64(self, v_int64: builtins.int) -> None: ...

    def set_long(self, v_long: builtins.int) -> None: ...

    def set_object(self, v_object: typing.Optional[Object]) -> None: ...

    def set_param(self, param: typing.Optional[ParamSpec]) -> None: ...

    def set_pointer(self, v_pointer: typing.Optional[builtins.object]) -> None: ...

    def set_schar(self, v_char: builtins.int) -> None: ...

    def set_static_boxed(self, v_boxed: typing.Optional[builtins.object]) -> None: ...

    def set_static_string(self, v_string: typing.Optional[builtins.str]) -> None: ...

    def set_string(self, v_string: typing.Optional[builtins.str]) -> None: ...

    def set_string_take_ownership(self, v_string: typing.Optional[builtins.str]) -> None: ...

    def set_uchar(self, v_uchar: builtins.int) -> None: ...

    def set_uint(self, v_uint: builtins.int) -> None: ...

    def set_uint64(self, v_uint64: builtins.int) -> None: ...

    def set_ulong(self, v_ulong: builtins.int) -> None: ...

    def set_variant(self, variant: typing.Optional[GLib.Variant]) -> None: ...

    def take_boxed(self, v_boxed: typing.Optional[builtins.object]) -> None: ...

    def take_string(self, v_string: typing.Optional[builtins.str]) -> None: ...

    def take_variant(self, variant: typing.Optional[GLib.Variant]) -> None: ...

    def transform(self, dest_value: Value) -> builtins.bool: ...

    @staticmethod
    def type_compatible(src_type: GType, dest_type: GType) -> builtins.bool: ...

    @staticmethod
    def type_transformable(src_type: GType, dest_type: GType) -> builtins.bool: ...

    def unset(self) -> None: ...


class ValueArray():
    n_prealloced: builtins.int
    n_values: builtins.int
    values: Value

    def append(self, value: typing.Optional[Value]) -> ValueArray: ...

    def copy(self) -> ValueArray: ...

    def get_nth(self, index_: builtins.int) -> Value: ...

    def insert(self, index_: builtins.int, value: typing.Optional[Value]) -> ValueArray: ...

    @staticmethod
    def new(n_prealloced: builtins.int) -> ValueArray: ...

    def prepend(self, value: typing.Optional[Value]) -> ValueArray: ...

    def remove(self, index_: builtins.int) -> ValueArray: ...

    def sort(self, compare_func: GLib.CompareDataFunc, *user_data: typing.Optional[builtins.object]) -> ValueArray: ...


class WeakRef():
    ...


class TypeCValue():
    ...


class BindingFlags(GFlags, builtins.int):
    BIDIRECTIONAL = ...  # type: BindingFlags
    DEFAULT = ...  # type: BindingFlags
    INVERT_BOOLEAN = ...  # type: BindingFlags
    SYNC_CREATE = ...  # type: BindingFlags


class ConnectFlags(GLib.Flags, builtins.int):
    AFTER = ...  # type: ConnectFlags
    SWAPPED = ...  # type: ConnectFlags


class GFlags(GLib.Flags, builtins.int):
    ...


class ParamFlags(GLib.Flags, builtins.int):
    CONSTRUCT = ...  # type: ParamFlags
    CONSTRUCT_ONLY = ...  # type: ParamFlags
    DEPRECATED = ...  # type: ParamFlags
    EXPLICIT_NOTIFY = ...  # type: ParamFlags
    LAX_VALIDATION = ...  # type: ParamFlags
    PRIVATE = ...  # type: ParamFlags
    READABLE = ...  # type: ParamFlags
    READWRITE = ...  # type: ParamFlags
    STATIC_BLURB = ...  # type: ParamFlags
    STATIC_NAME = ...  # type: ParamFlags
    STATIC_NICK = ...  # type: ParamFlags
    WRITABLE = ...  # type: ParamFlags


class SignalFlags(GLib.Flags, builtins.int):
    ACTION = ...  # type: SignalFlags
    DEPRECATED = ...  # type: SignalFlags
    DETAILED = ...  # type: SignalFlags
    MUST_COLLECT = ...  # type: SignalFlags
    NO_HOOKS = ...  # type: SignalFlags
    NO_RECURSE = ...  # type: SignalFlags
    RUN_CLEANUP = ...  # type: SignalFlags
    RUN_FIRST = ...  # type: SignalFlags
    RUN_LAST = ...  # type: SignalFlags


class SignalMatchType(GLib.Flags, builtins.int):
    CLOSURE = ...  # type: SignalMatchType
    DATA = ...  # type: SignalMatchType
    DETAIL = ...  # type: SignalMatchType
    FUNC = ...  # type: SignalMatchType
    ID = ...  # type: SignalMatchType
    UNBLOCKED = ...  # type: SignalMatchType


class TypeDebugFlags(GLib.Flags, builtins.int):
    INSTANCE_COUNT = ...  # type: TypeDebugFlags
    MASK = ...  # type: TypeDebugFlags
    NONE = ...  # type: TypeDebugFlags
    OBJECTS = ...  # type: TypeDebugFlags
    SIGNALS = ...  # type: TypeDebugFlags


class TypeFlags(GLib.Flags, builtins.int):
    ABSTRACT = ...  # type: TypeFlags
    VALUE_ABSTRACT = ...  # type: TypeFlags


class TypeFundamentalFlags(GLib.Flags, builtins.int):
    CLASSED = ...  # type: TypeFundamentalFlags
    DEEP_DERIVABLE = ...  # type: TypeFundamentalFlags
    DERIVABLE = ...  # type: TypeFundamentalFlags
    INSTANTIATABLE = ...  # type: TypeFundamentalFlags


class GEnum(GLib.Enum, builtins.int):
    ...


BaseFinalizeFunc = typing.Callable[[TypeClass], None]
BaseInitFunc = typing.Callable[[TypeClass], None]
BindingTransformFunc = typing.Callable[[Binding, Value, Value, typing.Optional[builtins.object]], builtins.bool]
BoxedCopyFunc = typing.Callable[[builtins.object], builtins.object]
BoxedFreeFunc = typing.Callable[[builtins.object], None]
Callback = typing.Callable[[], None]
ClassFinalizeFunc = typing.Callable[[TypeClass, typing.Optional[builtins.object]], None]
ClassInitFunc = typing.Callable[[TypeClass, typing.Optional[builtins.object]], None]
ClosureMarshal = typing.Callable[[Closure, typing.Optional[Value], typing.Sequence[Value], typing.Optional[builtins.object], typing.Optional[builtins.object]], None]
ClosureNotify = typing.Callable[[typing.Optional[builtins.object], Closure], None]
InstanceInitFunc = typing.Callable[[TypeInstance, TypeClass], None]
InterfaceFinalizeFunc = typing.Callable[[TypeInterface, typing.Optional[builtins.object]], None]
InterfaceInitFunc = typing.Callable[[TypeInterface, typing.Optional[builtins.object]], None]
ObjectFinalizeFunc = typing.Callable[[Object], None]
ObjectGetPropertyFunc = typing.Callable[[Object, builtins.int, Value, ParamSpec], None]
ObjectSetPropertyFunc = typing.Callable[[Object, builtins.int, Value, ParamSpec], None]
SignalAccumulator = typing.Callable[[SignalInvocationHint, Value, Value, typing.Optional[builtins.object]], builtins.bool]
SignalEmissionHook = typing.Callable[[SignalInvocationHint, typing.Sequence[Value], typing.Optional[builtins.object]], builtins.bool]
ToggleNotify = typing.Callable[[typing.Optional[builtins.object], Object, builtins.bool], None]
TypeClassCacheFunc = typing.Callable[[typing.Optional[builtins.object], TypeClass], builtins.bool]
TypeInterfaceCheckFunc = typing.Callable[[typing.Optional[builtins.object], TypeInterface], None]
TypePluginCompleteInterfaceInfo = typing.Callable[[TypePlugin, GType, GType, InterfaceInfo], None]
TypePluginCompleteTypeInfo = typing.Callable[[TypePlugin, GType, TypeInfo, TypeValueTable], None]
TypePluginUnuse = typing.Callable[[TypePlugin], None]
TypePluginUse = typing.Callable[[TypePlugin], None]
ValueTransform = typing.Callable[[Value, Value], None]
WeakNotify = typing.Callable[[typing.Optional[builtins.object], Object], None]


def boxed_copy(boxed_type: GType, src_boxed: builtins.object) -> builtins.object: ...


def boxed_free(boxed_type: GType, boxed: builtins.object) -> None: ...


def cclosure_marshal_BOOLEAN__BOXED_BOXED(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_BOOLEAN__FLAGS(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_STRING__OBJECT_POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__BOOLEAN(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__BOXED(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__CHAR(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__DOUBLE(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__ENUM(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__FLAGS(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__FLOAT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__INT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__LONG(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__OBJECT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__PARAM(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__STRING(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__UCHAR(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__UINT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__UINT_POINTER(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__ULONG(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__VARIANT(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_VOID__VOID(closure: Closure, return_value: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def cclosure_marshal_generic(closure: Closure, return_gvalue: Value, n_param_values: builtins.int, param_values: Value, invocation_hint: typing.Optional[builtins.object], marshal_data: typing.Optional[builtins.object]) -> None: ...


def clear_signal_handler(handler_id_ptr: builtins.int, instance: Object) -> None: ...


def enum_complete_type_info(g_enum_type: GType, const_values: EnumValue) -> TypeInfo: ...


def enum_get_value(enum_class: EnumClass, value: builtins.int) -> EnumValue: ...


def enum_get_value_by_name(enum_class: EnumClass, name: builtins.str) -> EnumValue: ...


def enum_get_value_by_nick(enum_class: EnumClass, nick: builtins.str) -> EnumValue: ...


def enum_register_static(name: builtins.str, const_static_values: EnumValue) -> GType: ...


def enum_to_string(g_enum_type: GType, value: builtins.int) -> builtins.str: ...


def flags_complete_type_info(g_flags_type: GType, const_values: FlagsValue) -> TypeInfo: ...


def flags_get_first_value(flags_class: FlagsClass, value: builtins.int) -> FlagsValue: ...


def flags_get_value_by_name(flags_class: FlagsClass, name: builtins.str) -> FlagsValue: ...


def flags_get_value_by_nick(flags_class: FlagsClass, nick: builtins.str) -> FlagsValue: ...


def flags_register_static(name: builtins.str, const_static_values: FlagsValue) -> GType: ...


def flags_to_string(flags_type: GType, value: builtins.int) -> builtins.str: ...


def gtype_get_type() -> GType: ...


def param_spec_boolean(name: builtins.str, nick: builtins.str, blurb: builtins.str, default_value: builtins.bool, flags: ParamFlags) -> ParamSpec: ...


def param_spec_boxed(name: builtins.str, nick: builtins.str, blurb: builtins.str, boxed_type: GType, flags: ParamFlags) -> ParamSpec: ...


def param_spec_char(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_double(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.float, maximum: builtins.float, default_value: builtins.float, flags: ParamFlags) -> ParamSpec: ...


def param_spec_enum(name: builtins.str, nick: builtins.str, blurb: builtins.str, enum_type: GType, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_flags(name: builtins.str, nick: builtins.str, blurb: builtins.str, flags_type: GType, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_float(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.float, maximum: builtins.float, default_value: builtins.float, flags: ParamFlags) -> ParamSpec: ...


def param_spec_gtype(name: builtins.str, nick: builtins.str, blurb: builtins.str, is_a_type: GType, flags: ParamFlags) -> ParamSpec: ...


def param_spec_int(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_int64(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_long(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_object(name: builtins.str, nick: builtins.str, blurb: builtins.str, object_type: GType, flags: ParamFlags) -> ParamSpec: ...


def param_spec_param(name: builtins.str, nick: builtins.str, blurb: builtins.str, param_type: GType, flags: ParamFlags) -> ParamSpec: ...


def param_spec_pointer(name: builtins.str, nick: builtins.str, blurb: builtins.str, flags: ParamFlags) -> ParamSpec: ...


def param_spec_pool_new(type_prefixing: builtins.bool) -> ParamSpecPool: ...


def param_spec_string(name: builtins.str, nick: builtins.str, blurb: builtins.str, default_value: typing.Optional[builtins.str], flags: ParamFlags) -> ParamSpec: ...


def param_spec_uchar(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_uint(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_uint64(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_ulong(name: builtins.str, nick: builtins.str, blurb: builtins.str, minimum: builtins.int, maximum: builtins.int, default_value: builtins.int, flags: ParamFlags) -> ParamSpec: ...


def param_spec_unichar(name: builtins.str, nick: builtins.str, blurb: builtins.str, default_value: builtins.str, flags: ParamFlags) -> ParamSpec: ...


def param_spec_variant(name: builtins.str, nick: builtins.str, blurb: builtins.str, type: GLib.VariantType, default_value: typing.Optional[GLib.Variant], flags: ParamFlags) -> ParamSpec: ...


def param_type_register_static(name: builtins.str, pspec_info: ParamSpecTypeInfo) -> GType: ...


def param_value_convert(pspec: ParamSpec, src_value: Value, dest_value: Value, strict_validation: builtins.bool) -> builtins.bool: ...


def param_value_defaults(pspec: ParamSpec, value: Value) -> builtins.bool: ...


def param_value_set_default(pspec: ParamSpec, value: Value) -> None: ...


def param_value_validate(pspec: ParamSpec, value: Value) -> builtins.bool: ...


def param_values_cmp(pspec: ParamSpec, value1: Value, value2: Value) -> builtins.int: ...


def pointer_type_register_static(name: builtins.str) -> GType: ...


def signal_accumulator_first_wins(ihint: SignalInvocationHint, return_accu: Value, handler_return: Value, dummy: typing.Optional[builtins.object]) -> builtins.bool: ...


def signal_accumulator_true_handled(ihint: SignalInvocationHint, return_accu: Value, handler_return: Value, dummy: typing.Optional[builtins.object]) -> builtins.bool: ...


def signal_add_emission_hook(signal_id: builtins.int, detail: builtins.int, hook_func: SignalEmissionHook, *hook_data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_chain_from_overridden(instance_and_params: typing.Sequence[Value], return_value: Value) -> None: ...


def signal_connect_closure(instance: Object, detailed_signal: builtins.str, closure: Closure, after: builtins.bool) -> builtins.int: ...


def signal_connect_closure_by_id(instance: Object, signal_id: builtins.int, detail: builtins.int, closure: Closure, after: builtins.bool) -> builtins.int: ...


def signal_emitv(instance_and_params: typing.Sequence[Value], signal_id: builtins.int, detail: builtins.int, return_value: Value) -> Value: ...


def signal_get_invocation_hint(instance: Object) -> SignalInvocationHint: ...


def signal_handler_block(instance: Object, handler_id: builtins.int) -> None: ...


def signal_handler_disconnect(instance: Object, handler_id: builtins.int) -> None: ...


def signal_handler_find(instance: Object, mask: SignalMatchType, signal_id: builtins.int, detail: builtins.int, closure: typing.Optional[Closure], func: typing.Optional[builtins.object], data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_handler_is_connected(instance: Object, handler_id: builtins.int) -> builtins.bool: ...


def signal_handler_unblock(instance: Object, handler_id: builtins.int) -> None: ...


def signal_handlers_block_matched(instance: Object, mask: SignalMatchType, signal_id: builtins.int, detail: builtins.int, closure: typing.Optional[Closure], func: typing.Optional[builtins.object], data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_handlers_destroy(instance: Object) -> None: ...


def signal_handlers_disconnect_matched(instance: Object, mask: SignalMatchType, signal_id: builtins.int, detail: builtins.int, closure: typing.Optional[Closure], func: typing.Optional[builtins.object], data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_handlers_unblock_matched(instance: Object, mask: SignalMatchType, signal_id: builtins.int, detail: builtins.int, closure: typing.Optional[Closure], func: typing.Optional[builtins.object], data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_has_handler_pending(instance: Object, signal_id: builtins.int, detail: builtins.int, may_be_blocked: builtins.bool) -> builtins.bool: ...


def signal_list_ids(itype: GType) -> typing.Sequence[builtins.int]: ...


def signal_lookup(name: builtins.str, itype: GType) -> builtins.int: ...


def signal_name(signal_id: builtins.int) -> builtins.str: ...


def signal_override_class_closure(signal_id: builtins.int, instance_type: GType, class_closure: Closure) -> None: ...


def signal_parse_name(detailed_signal: builtins.str, itype: GType, force_detail_quark: builtins.bool) -> typing.Tuple[builtins.bool, builtins.int, builtins.int]: ...


def signal_query(signal_id: builtins.int) -> SignalQuery: ...


def signal_remove_emission_hook(signal_id: builtins.int, hook_id: builtins.int) -> None: ...


def signal_stop_emission(instance: Object, signal_id: builtins.int, detail: builtins.int) -> None: ...


def signal_stop_emission_by_name(instance: Object, detailed_signal: builtins.str) -> None: ...


def signal_type_cclosure_new(itype: GType, struct_offset: builtins.int) -> Closure: ...


def source_set_closure(source: GLib.Source, closure: Closure) -> None: ...


def source_set_dummy_callback(source: GLib.Source) -> None: ...


def strdup_value_contents(value: Value) -> builtins.str: ...


def type_add_class_private(class_type: GType, private_size: builtins.int) -> None: ...


def type_add_instance_private(class_type: GType, private_size: builtins.int) -> builtins.int: ...


def type_add_interface_dynamic(instance_type: GType, interface_type: GType, plugin: TypePlugin) -> None: ...


def type_add_interface_static(instance_type: GType, interface_type: GType, info: InterfaceInfo) -> None: ...


def type_check_class_is_a(g_class: TypeClass, is_a_type: GType) -> builtins.bool: ...


def type_check_instance(instance: TypeInstance) -> builtins.bool: ...


def type_check_instance_is_a(instance: TypeInstance, iface_type: GType) -> builtins.bool: ...


def type_check_instance_is_fundamentally_a(instance: TypeInstance, fundamental_type: GType) -> builtins.bool: ...


def type_check_is_value_type(type: GType) -> builtins.bool: ...


def type_check_value(value: Value) -> builtins.bool: ...


def type_check_value_holds(value: Value, type: GType) -> builtins.bool: ...


def type_children(type: GType) -> typing.Sequence[GType]: ...


def type_class_adjust_private_offset(g_class: typing.Optional[builtins.object], private_size_or_offset: builtins.int) -> None: ...


def type_class_peek(type: GType) -> TypeClass: ...


def type_class_peek_static(type: GType) -> TypeClass: ...


def type_class_ref(type: GType) -> TypeClass: ...


def type_default_interface_peek(g_type: GType) -> TypeInterface: ...


def type_default_interface_ref(g_type: GType) -> TypeInterface: ...


def type_default_interface_unref(g_iface: TypeInterface) -> None: ...


def type_depth(type: GType) -> builtins.int: ...


def type_ensure(type: GType) -> None: ...


def type_free_instance(instance: TypeInstance) -> None: ...


def type_from_name(name: builtins.str) -> GType: ...


def type_fundamental(type_id: GType) -> GType: ...


def type_fundamental_next() -> GType: ...


def type_get_instance_count(type: GType) -> builtins.int: ...


def type_get_plugin(type: GType) -> TypePlugin: ...


def type_get_qdata(type: GType, quark: builtins.int) -> typing.Optional[builtins.object]: ...


def type_get_type_registration_serial() -> builtins.int: ...


def type_init() -> None: ...


def type_init_with_debug_flags(debug_flags: TypeDebugFlags) -> None: ...


def type_interface_add_prerequisite(interface_type: GType, prerequisite_type: GType) -> None: ...


def type_interface_get_plugin(instance_type: GType, interface_type: GType) -> TypePlugin: ...


def type_interface_peek(instance_class: TypeClass, iface_type: GType) -> TypeInterface: ...


def type_interface_prerequisites(interface_type: GType) -> typing.Sequence[GType]: ...


def type_interfaces(type: GType) -> typing.Sequence[GType]: ...


def type_is_a(type: GType, is_a_type: GType) -> builtins.bool: ...


def type_name(type: GType) -> builtins.str: ...


def type_name_from_class(g_class: TypeClass) -> builtins.str: ...


def type_name_from_instance(instance: TypeInstance) -> builtins.str: ...


def type_next_base(leaf_type: GType, root_type: GType) -> GType: ...


def type_parent(type: GType) -> GType: ...


def type_qname(type: GType) -> builtins.int: ...


def type_query(type: GType) -> TypeQuery: ...


def type_register_dynamic(parent_type: GType, type_name: builtins.str, plugin: TypePlugin, flags: TypeFlags) -> GType: ...


def type_register_fundamental(type_id: GType, type_name: builtins.str, info: TypeInfo, finfo: TypeFundamentalInfo, flags: TypeFlags) -> GType: ...


def type_register_static(parent_type: GType, type_name: builtins.str, info: TypeInfo, flags: TypeFlags) -> GType: ...


def type_set_qdata(type: GType, quark: builtins.int, data: typing.Optional[builtins.object]) -> None: ...


def type_test_flags(type: GType, flags: builtins.int) -> builtins.bool: ...


def value_type_compatible(src_type: GType, dest_type: GType) -> builtins.bool: ...


def value_type_transformable(src_type: GType, dest_type: GType) -> builtins.bool: ...


GBoxed: typing.Any
GObjectWeakRef: typing.Any
GParamSpec: typing.Any
GPointer: typing.Any
G_MAXDOUBLE: builtins.float
G_MAXFLOAT: builtins.float
G_MAXINT: builtins.int
G_MAXINT16: builtins.int
G_MAXINT32: builtins.int
G_MAXINT64: builtins.int
G_MAXINT8: builtins.int
G_MAXLONG: builtins.int
G_MAXOFFSET: builtins.int
G_MAXSHORT: builtins.int
G_MAXSIZE: builtins.int
G_MAXSSIZE: builtins.int
G_MAXUINT: builtins.int
G_MAXUINT16: builtins.int
G_MAXUINT32: builtins.int
G_MAXUINT64: builtins.int
G_MAXUINT8: builtins.int
G_MAXULONG: builtins.int
G_MAXUSHORT: builtins.int
G_MINDOUBLE: builtins.float
G_MINFLOAT: builtins.float
G_MININT: builtins.int
G_MININT16: builtins.int
G_MININT32: builtins.int
G_MININT64: builtins.int
G_MININT8: builtins.int
G_MINLONG: builtins.int
G_MINOFFSET: builtins.int
G_MINSHORT: builtins.int
G_MINSSIZE: builtins.int
IO_ERR: GLib.IOCondition
IO_FLAG_APPEND: GLib.IOFlags
IO_FLAG_GET_MASK: GLib.IOFlags
IO_FLAG_IS_READABLE: GLib.IOFlags
IO_FLAG_IS_SEEKABLE: GLib.IOFlags
IO_FLAG_IS_WRITEABLE: GLib.IOFlags
IO_FLAG_MASK: GLib.IOFlags
IO_FLAG_NONBLOCK: GLib.IOFlags
IO_FLAG_SET_MASK: GLib.IOFlags
IO_HUP: GLib.IOCondition
IO_IN: GLib.IOCondition
IO_NVAL: GLib.IOCondition
IO_OUT: GLib.IOCondition
IO_PRI: GLib.IOCondition
IO_STATUS_AGAIN: GLib.IOStatus
IO_STATUS_EOF: GLib.IOStatus
IO_STATUS_ERROR: GLib.IOStatus
IO_STATUS_NORMAL: GLib.IOStatus
OPTION_ERROR_BAD_VALUE: GLib.OptionError
OPTION_ERROR_FAILED: GLib.OptionError
OPTION_ERROR_UNKNOWN_OPTION: GLib.OptionError
OPTION_FLAG_FILENAME: GLib.OptionFlags
OPTION_FLAG_HIDDEN: GLib.OptionFlags
OPTION_FLAG_IN_MAIN: GLib.OptionFlags
OPTION_FLAG_NOALIAS: GLib.OptionFlags
OPTION_FLAG_NO_ARG: GLib.OptionFlags
OPTION_FLAG_OPTIONAL_ARG: GLib.OptionFlags
OPTION_FLAG_REVERSE: GLib.OptionFlags
OPTION_REMAINING: builtins.str
PARAM_CONSTRUCT: ParamFlags
PARAM_CONSTRUCT_ONLY: ParamFlags
PARAM_LAX_VALIDATION: ParamFlags
PARAM_MASK: builtins.int
PARAM_READABLE: ParamFlags
PARAM_READWRITE: ParamFlags
PARAM_STATIC_STRINGS: builtins.int
PARAM_USER_SHIFT: builtins.int
PARAM_WRITABLE: ParamFlags
PRIORITY_DEFAULT: builtins.int
PRIORITY_DEFAULT_IDLE: builtins.int
PRIORITY_HIGH: builtins.int
PRIORITY_HIGH_IDLE: builtins.int
PRIORITY_LOW: builtins.int
SIGNAL_ACTION: SignalFlags
SIGNAL_DETAILED: SignalFlags
SIGNAL_FLAGS_MASK: builtins.int
SIGNAL_MATCH_MASK: builtins.int
SIGNAL_NO_HOOKS: SignalFlags
SIGNAL_NO_RECURSE: SignalFlags
SIGNAL_RUN_CLEANUP: SignalFlags
SIGNAL_RUN_FIRST: SignalFlags
SIGNAL_RUN_LAST: SignalFlags
SPAWN_CHILD_INHERITS_STDIN: GLib.SpawnFlags
SPAWN_DO_NOT_REAP_CHILD: GLib.SpawnFlags
SPAWN_FILE_AND_ARGV_ZERO: GLib.SpawnFlags
SPAWN_LEAVE_DESCRIPTORS_OPEN: GLib.SpawnFlags
SPAWN_SEARCH_PATH: GLib.SpawnFlags
SPAWN_STDERR_TO_DEV_NULL: GLib.SpawnFlags
SPAWN_STDOUT_TO_DEV_NULL: GLib.SpawnFlags
TYPE_BOOLEAN: GType
TYPE_BOXED: GType
TYPE_CHAR: GType
TYPE_DOUBLE: GType
TYPE_ENUM: GType
TYPE_FLAGS: GType
TYPE_FLAG_RESERVED_ID_BIT: builtins.int
TYPE_FLOAT: GType
TYPE_FUNDAMENTAL_MAX: builtins.int
TYPE_FUNDAMENTAL_SHIFT: builtins.int
TYPE_GSTRING: GType
TYPE_GTYPE: GType
TYPE_INT: GType
TYPE_INT64: GType
TYPE_INTERFACE: GType
TYPE_INVALID: GType
TYPE_LONG: GType
TYPE_NONE: GType
TYPE_OBJECT: GType
TYPE_PARAM: GType
TYPE_POINTER: GType
TYPE_PYOBJECT: GType
TYPE_RESERVED_BSE_FIRST: builtins.int
TYPE_RESERVED_BSE_LAST: builtins.int
TYPE_RESERVED_GLIB_FIRST: builtins.int
TYPE_RESERVED_GLIB_LAST: builtins.int
TYPE_RESERVED_USER_FIRST: builtins.int
TYPE_STRING: GType
TYPE_STRV: GType
TYPE_UCHAR: GType
TYPE_UINT: GType
TYPE_UINT64: GType
TYPE_ULONG: GType
TYPE_UNICHAR: GType
TYPE_VALUE: GType
TYPE_VARIANT: GType
VALUE_NOCOPY_CONTENTS: builtins.int
Warning: typing.Any
features: typing.Dict[str, bool]
glib_version: typing.Tuple[int, int, int]
pygobject_version: typing.Tuple[int, int, int]


GObject = Object
