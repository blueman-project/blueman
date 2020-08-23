import builtins
import typing

from gi.repository import GObject


FlagsT = typing.TypeVar('FlagsT')


class Error(RuntimeError):
    message: str


class Array():
    data: builtins.str
    len: builtins.int


class AsyncQueue():

    def length(self) -> builtins.int: ...

    def length_unlocked(self) -> builtins.int: ...

    def lock(self) -> None: ...

    def pop(self) -> typing.Optional[builtins.object]: ...

    def pop_unlocked(self) -> typing.Optional[builtins.object]: ...

    def push(self, data: typing.Optional[builtins.object]) -> None: ...

    def push_front(self, item: typing.Optional[builtins.object]) -> None: ...

    def push_front_unlocked(self, item: typing.Optional[builtins.object]) -> None: ...

    def push_unlocked(self, data: typing.Optional[builtins.object]) -> None: ...

    def ref_unlocked(self) -> None: ...

    def remove(self, item: typing.Optional[builtins.object]) -> builtins.bool: ...

    def remove_unlocked(self, item: typing.Optional[builtins.object]) -> builtins.bool: ...

    def timed_pop(self, end_time: TimeVal) -> typing.Optional[builtins.object]: ...

    def timed_pop_unlocked(self, end_time: TimeVal) -> typing.Optional[builtins.object]: ...

    def timeout_pop(self, timeout: builtins.int) -> typing.Optional[builtins.object]: ...

    def timeout_pop_unlocked(self, timeout: builtins.int) -> typing.Optional[builtins.object]: ...

    def try_pop(self) -> typing.Optional[builtins.object]: ...

    def try_pop_unlocked(self) -> typing.Optional[builtins.object]: ...

    def unlock(self) -> None: ...

    def unref(self) -> None: ...

    def unref_and_unlock(self) -> None: ...


class BookmarkFile():

    def add_application(self, uri: builtins.str, name: typing.Optional[builtins.str], exec_: typing.Optional[builtins.str]) -> None: ...

    def add_group(self, uri: builtins.str, group: builtins.str) -> None: ...

    @staticmethod
    def error_quark() -> builtins.int: ...

    def free(self) -> None: ...

    def get_added(self, uri: builtins.str) -> builtins.int: ...

    def get_app_info(self, uri: builtins.str, name: builtins.str) -> typing.Tuple[builtins.bool, builtins.str, builtins.int, builtins.int]: ...

    def get_applications(self, uri: builtins.str) -> typing.Sequence[builtins.str]: ...

    def get_description(self, uri: builtins.str) -> builtins.str: ...

    def get_groups(self, uri: builtins.str) -> typing.Sequence[builtins.str]: ...

    def get_icon(self, uri: builtins.str) -> typing.Tuple[builtins.bool, builtins.str, builtins.str]: ...

    def get_is_private(self, uri: builtins.str) -> builtins.bool: ...

    def get_mime_type(self, uri: builtins.str) -> builtins.str: ...

    def get_modified(self, uri: builtins.str) -> builtins.int: ...

    def get_size(self) -> builtins.int: ...

    def get_title(self, uri: typing.Optional[builtins.str]) -> builtins.str: ...

    def get_uris(self) -> typing.Sequence[builtins.str]: ...

    def get_visited(self, uri: builtins.str) -> builtins.int: ...

    def has_application(self, uri: builtins.str, name: builtins.str) -> builtins.bool: ...

    def has_group(self, uri: builtins.str, group: builtins.str) -> builtins.bool: ...

    def has_item(self, uri: builtins.str) -> builtins.bool: ...

    def load_from_data(self, data: builtins.bytes) -> builtins.bool: ...

    def load_from_data_dirs(self, file: builtins.str) -> typing.Tuple[builtins.bool, builtins.str]: ...

    def load_from_file(self, filename: builtins.str) -> builtins.bool: ...

    def move_item(self, old_uri: builtins.str, new_uri: typing.Optional[builtins.str]) -> builtins.bool: ...

    def remove_application(self, uri: builtins.str, name: builtins.str) -> builtins.bool: ...

    def remove_group(self, uri: builtins.str, group: builtins.str) -> builtins.bool: ...

    def remove_item(self, uri: builtins.str) -> builtins.bool: ...

    def set_added(self, uri: builtins.str, added: builtins.int) -> None: ...

    def set_app_info(self, uri: builtins.str, name: builtins.str, exec_: builtins.str, count: builtins.int, stamp: builtins.int) -> builtins.bool: ...

    def set_description(self, uri: typing.Optional[builtins.str], description: builtins.str) -> None: ...

    def set_groups(self, uri: builtins.str, groups: typing.Optional[typing.Sequence[builtins.str]]) -> None: ...

    def set_icon(self, uri: builtins.str, href: typing.Optional[builtins.str], mime_type: builtins.str) -> None: ...

    def set_is_private(self, uri: builtins.str, is_private: builtins.bool) -> None: ...

    def set_mime_type(self, uri: builtins.str, mime_type: builtins.str) -> None: ...

    def set_modified(self, uri: builtins.str, modified: builtins.int) -> None: ...

    def set_title(self, uri: typing.Optional[builtins.str], title: builtins.str) -> None: ...

    def set_visited(self, uri: builtins.str, visited: builtins.int) -> None: ...

    def to_data(self) -> builtins.bytes: ...

    def to_file(self, filename: builtins.str) -> builtins.bool: ...


class ByteArray():
    data: builtins.int
    len: builtins.int

    @staticmethod
    def free(array: builtins.bytes, free_segment: builtins.bool) -> builtins.int: ...

    @staticmethod
    def free_to_bytes(array: builtins.bytes) -> Bytes: ...

    @staticmethod
    def new() -> builtins.bytes: ...

    @staticmethod
    def new_take(data: builtins.bytes) -> builtins.bytes: ...

    @staticmethod
    def steal(array: builtins.bytes) -> typing.Tuple[builtins.int, builtins.int]: ...

    @staticmethod
    def unref(array: builtins.bytes) -> None: ...


class Bytes():

    def compare(self, bytes2: Bytes) -> builtins.int: ...

    def equal(self, bytes2: Bytes) -> builtins.bool: ...

    def get_data(self) -> typing.Optional[builtins.bytes]: ...

    def get_size(self) -> builtins.int: ...

    def hash(self) -> builtins.int: ...

    @staticmethod
    def new(data: typing.Optional[builtins.bytes]) -> Bytes: ...

    def new_from_bytes(self, offset: builtins.int, length: builtins.int) -> Bytes: ...

    @staticmethod
    def new_take(data: typing.Optional[builtins.bytes]) -> Bytes: ...

    def ref(self) -> Bytes: ...

    def unref(self) -> None: ...

    def unref_to_array(self) -> builtins.bytes: ...

    def unref_to_data(self) -> builtins.bytes: ...


class Checksum():

    def copy(self) -> Checksum: ...

    def free(self) -> None: ...

    def get_string(self) -> builtins.str: ...

    @staticmethod
    def new(checksum_type: ChecksumType) -> Checksum: ...

    def reset(self) -> None: ...

    @staticmethod
    def type_get_length(checksum_type: ChecksumType) -> builtins.int: ...

    def update(self, data: builtins.bytes) -> None: ...


class Cond():
    i: typing.Sequence[builtins.int]
    p: builtins.object

    def broadcast(self) -> None: ...

    def clear(self) -> None: ...

    def init(self) -> None: ...

    def signal(self) -> None: ...

    def wait(self, mutex: Mutex) -> None: ...

    def wait_until(self, mutex: Mutex, end_time: builtins.int) -> builtins.bool: ...


class Data():
    ...


class Date():
    day: builtins.int
    dmy: builtins.int
    julian: builtins.int
    julian_days: builtins.int
    month: builtins.int
    year: builtins.int

    def add_days(self, n_days: builtins.int) -> None: ...

    def add_months(self, n_months: builtins.int) -> None: ...

    def add_years(self, n_years: builtins.int) -> None: ...

    def clamp(self, min_date: Date, max_date: Date) -> None: ...

    def clear(self, n_dates: builtins.int) -> None: ...

    def compare(self, rhs: Date) -> builtins.int: ...

    def copy(self) -> Date: ...

    def days_between(self, date2: Date) -> builtins.int: ...

    def free(self) -> None: ...

    def get_day(self) -> builtins.int: ...

    def get_day_of_year(self) -> builtins.int: ...

    @staticmethod
    def get_days_in_month(month: DateMonth, year: builtins.int) -> builtins.int: ...

    def get_iso8601_week_of_year(self) -> builtins.int: ...

    def get_julian(self) -> builtins.int: ...

    def get_monday_week_of_year(self) -> builtins.int: ...

    @staticmethod
    def get_monday_weeks_in_year(year: builtins.int) -> builtins.int: ...

    def get_month(self) -> DateMonth: ...

    def get_sunday_week_of_year(self) -> builtins.int: ...

    @staticmethod
    def get_sunday_weeks_in_year(year: builtins.int) -> builtins.int: ...

    def get_weekday(self) -> DateWeekday: ...

    def get_year(self) -> builtins.int: ...

    def is_first_of_month(self) -> builtins.bool: ...

    def is_last_of_month(self) -> builtins.bool: ...

    @staticmethod
    def is_leap_year(year: builtins.int) -> builtins.bool: ...

    @staticmethod
    def new() -> Date: ...

    @staticmethod
    def new_dmy(day: builtins.int, month: DateMonth, year: builtins.int) -> Date: ...

    @staticmethod
    def new_julian(julian_day: builtins.int) -> Date: ...

    def order(self, date2: Date) -> None: ...

    def set_day(self, day: builtins.int) -> None: ...

    def set_dmy(self, day: builtins.int, month: DateMonth, y: builtins.int) -> None: ...

    def set_julian(self, julian_date: builtins.int) -> None: ...

    def set_month(self, month: DateMonth) -> None: ...

    def set_parse(self, str: builtins.str) -> None: ...

    def set_time(self, time_: builtins.int) -> None: ...

    def set_time_t(self, timet: builtins.int) -> None: ...

    def set_time_val(self, timeval: TimeVal) -> None: ...

    def set_year(self, year: builtins.int) -> None: ...

    @staticmethod
    def strftime(s: builtins.str, slen: builtins.int, format: builtins.str, date: Date) -> builtins.int: ...

    def subtract_days(self, n_days: builtins.int) -> None: ...

    def subtract_months(self, n_months: builtins.int) -> None: ...

    def subtract_years(self, n_years: builtins.int) -> None: ...

    def to_struct_tm(self, tm: builtins.object) -> None: ...

    def valid(self) -> builtins.bool: ...

    @staticmethod
    def valid_day(day: builtins.int) -> builtins.bool: ...

    @staticmethod
    def valid_dmy(day: builtins.int, month: DateMonth, year: builtins.int) -> builtins.bool: ...

    @staticmethod
    def valid_julian(julian_date: builtins.int) -> builtins.bool: ...

    @staticmethod
    def valid_month(month: DateMonth) -> builtins.bool: ...

    @staticmethod
    def valid_weekday(weekday: DateWeekday) -> builtins.bool: ...

    @staticmethod
    def valid_year(year: builtins.int) -> builtins.bool: ...


class DateTime():

    def add(self, timespan: builtins.int) -> DateTime: ...

    def add_days(self, days: builtins.int) -> DateTime: ...

    def add_full(self, years: builtins.int, months: builtins.int, days: builtins.int, hours: builtins.int, minutes: builtins.int, seconds: builtins.float) -> DateTime: ...

    def add_hours(self, hours: builtins.int) -> DateTime: ...

    def add_minutes(self, minutes: builtins.int) -> DateTime: ...

    def add_months(self, months: builtins.int) -> DateTime: ...

    def add_seconds(self, seconds: builtins.float) -> DateTime: ...

    def add_weeks(self, weeks: builtins.int) -> DateTime: ...

    def add_years(self, years: builtins.int) -> DateTime: ...

    @staticmethod
    def compare(dt1: builtins.object, dt2: builtins.object) -> builtins.int: ...

    def difference(self, begin: DateTime) -> builtins.int: ...

    @staticmethod
    def equal(dt1: builtins.object, dt2: builtins.object) -> builtins.bool: ...

    def format(self, format: builtins.str) -> builtins.str: ...

    def format_iso8601(self) -> builtins.str: ...

    def get_day_of_month(self) -> builtins.int: ...

    def get_day_of_week(self) -> builtins.int: ...

    def get_day_of_year(self) -> builtins.int: ...

    def get_hour(self) -> builtins.int: ...

    def get_microsecond(self) -> builtins.int: ...

    def get_minute(self) -> builtins.int: ...

    def get_month(self) -> builtins.int: ...

    def get_second(self) -> builtins.int: ...

    def get_seconds(self) -> builtins.float: ...

    def get_timezone(self) -> TimeZone: ...

    def get_timezone_abbreviation(self) -> builtins.str: ...

    def get_utc_offset(self) -> builtins.int: ...

    def get_week_numbering_year(self) -> builtins.int: ...

    def get_week_of_year(self) -> builtins.int: ...

    def get_year(self) -> builtins.int: ...

    def get_ymd(self) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...

    @staticmethod
    def hash(datetime: builtins.object) -> builtins.int: ...

    def is_daylight_savings(self) -> builtins.bool: ...

    @staticmethod
    def new(tz: TimeZone, year: builtins.int, month: builtins.int, day: builtins.int, hour: builtins.int, minute: builtins.int, seconds: builtins.float) -> DateTime: ...

    @staticmethod
    def new_from_iso8601(text: builtins.str, default_tz: typing.Optional[TimeZone]) -> typing.Optional[DateTime]: ...

    @staticmethod
    def new_from_timeval_local(tv: TimeVal) -> DateTime: ...

    @staticmethod
    def new_from_timeval_utc(tv: TimeVal) -> DateTime: ...

    @staticmethod
    def new_from_unix_local(t: builtins.int) -> DateTime: ...

    @staticmethod
    def new_from_unix_utc(t: builtins.int) -> DateTime: ...

    @staticmethod
    def new_local(year: builtins.int, month: builtins.int, day: builtins.int, hour: builtins.int, minute: builtins.int, seconds: builtins.float) -> DateTime: ...

    @staticmethod
    def new_now(tz: TimeZone) -> DateTime: ...

    @staticmethod
    def new_now_local() -> DateTime: ...

    @staticmethod
    def new_now_utc() -> DateTime: ...

    @staticmethod
    def new_utc(year: builtins.int, month: builtins.int, day: builtins.int, hour: builtins.int, minute: builtins.int, seconds: builtins.float) -> DateTime: ...

    def ref(self) -> DateTime: ...

    def to_local(self) -> DateTime: ...

    def to_timeval(self, tv: TimeVal) -> builtins.bool: ...

    def to_timezone(self, tz: TimeZone) -> DateTime: ...

    def to_unix(self) -> builtins.int: ...

    def to_utc(self) -> DateTime: ...

    def unref(self) -> None: ...


class DebugKey():
    key: builtins.str
    value: builtins.int


class Dir():

    def close(self) -> None: ...

    @staticmethod
    def make_tmp(tmpl: typing.Optional[builtins.str]) -> builtins.str: ...

    def read_name(self) -> builtins.str: ...

    def rewind(self) -> None: ...


class HashTable():

    @staticmethod
    def add(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def contains(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def destroy(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...

    @staticmethod
    def insert(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def lookup(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> typing.Optional[builtins.object]: ...

    @staticmethod
    def lookup_extended(hash_table: typing.Mapping[builtins.object, builtins.object], lookup_key: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...

    @staticmethod
    def remove(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def remove_all(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...

    @staticmethod
    def replace(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def size(hash_table: typing.Mapping[builtins.object, builtins.object]) -> builtins.int: ...

    @staticmethod
    def steal(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def steal_all(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...

    @staticmethod
    def steal_extended(hash_table: typing.Mapping[builtins.object, builtins.object], lookup_key: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...

    @staticmethod
    def unref(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...


class HashTableIter():
    dummy1: builtins.object
    dummy2: builtins.object
    dummy3: builtins.object
    dummy4: builtins.int
    dummy5: builtins.bool
    dummy6: builtins.object

    def init(self, hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...

    def next(self) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...

    def remove(self) -> None: ...

    def replace(self, value: typing.Optional[builtins.object]) -> None: ...

    def steal(self) -> None: ...


class Hmac():

    def get_digest(self, buffer: builtins.bytes) -> None: ...

    def get_string(self) -> builtins.str: ...

    def unref(self) -> None: ...

    def update(self, data: builtins.bytes) -> None: ...


class Hook():
    data: builtins.object
    destroy: DestroyNotify
    flags: builtins.int
    func: builtins.object
    hook_id: builtins.int
    next: Hook
    prev: Hook
    ref_count: builtins.int

    def compare_ids(self, sibling: Hook) -> builtins.int: ...

    @staticmethod
    def destroy_link(hook_list: HookList, hook: Hook) -> None: ...

    @staticmethod
    def free(hook_list: HookList, hook: Hook) -> None: ...

    @staticmethod
    def insert_before(hook_list: HookList, sibling: typing.Optional[Hook], hook: Hook) -> None: ...

    @staticmethod
    def prepend(hook_list: HookList, hook: Hook) -> None: ...

    @staticmethod
    def unref(hook_list: HookList, hook: Hook) -> None: ...


class HookList():
    dummy3: builtins.object
    dummy: typing.Sequence[builtins.object]
    finalize_hook: HookFinalizeFunc
    hook_size: builtins.int
    hooks: Hook
    is_setup: builtins.int
    seq_id: builtins.int

    def clear(self) -> None: ...

    def init(self, hook_size: builtins.int) -> None: ...

    def invoke(self, may_recurse: builtins.bool) -> None: ...

    def invoke_check(self, may_recurse: builtins.bool) -> None: ...


class IOChannel():
    buf_size: builtins.int
    close_on_unref: builtins.int
    do_encode: builtins.int
    encoded_read_buf: String
    encoding: builtins.str
    funcs: IOFuncs
    is_readable: builtins.int
    is_seekable: builtins.int
    is_writeable: builtins.int
    line_term: builtins.str
    line_term_len: builtins.int
    partial_write_buf: typing.Sequence[builtins.int]
    read_buf: String
    read_cd: builtins.object
    ref_count: builtins.int
    reserved1: builtins.object
    reserved2: builtins.object
    use_buffer: builtins.int
    write_buf: String
    write_cd: builtins.object

    def close(self) -> None: ...

    @staticmethod
    def error_from_errno(en: builtins.int) -> IOChannelError: ...

    @staticmethod
    def error_quark() -> builtins.int: ...

    def flush(self) -> IOStatus: ...

    def get_buffer_condition(self) -> IOCondition: ...

    def get_buffer_size(self) -> builtins.int: ...

    def get_buffered(self) -> builtins.bool: ...

    def get_close_on_unref(self) -> builtins.bool: ...

    def get_encoding(self) -> builtins.str: ...

    def get_flags(self) -> IOFlags: ...

    def get_line_term(self, length: builtins.int) -> builtins.str: ...

    def init(self) -> None: ...

    @staticmethod
    def new_file(filename: builtins.str, mode: builtins.str) -> IOChannel: ...

    def read(self, max_count: int = -1) -> bytes: ...

    def read_chars(self) -> typing.Tuple[IOStatus, builtins.bytes, builtins.int]: ...

    def read_line(self) -> typing.Tuple[IOStatus, builtins.str, builtins.int, builtins.int]: ...

    def read_line_string(self, buffer: String, terminator_pos: typing.Optional[builtins.int]) -> IOStatus: ...

    def read_to_end(self) -> typing.Tuple[IOStatus, builtins.bytes]: ...

    def read_unichar(self) -> typing.Tuple[IOStatus, builtins.str]: ...

    def readline(self) -> str: ...

    def ref(self) -> IOChannel: ...

    def seek(self, offset: builtins.int, type: SeekType) -> IOError: ...

    def seek_position(self, offset: builtins.int, type: SeekType) -> IOStatus: ...

    def set_buffer_size(self, size: builtins.int) -> None: ...

    def set_buffered(self, buffered: builtins.bool) -> None: ...

    def set_close_on_unref(self, do_close: builtins.bool) -> None: ...

    def set_encoding(self, encoding: typing.Optional[builtins.str]) -> IOStatus: ...

    def set_flags(self, flags: IOFlags) -> IOStatus: ...

    def set_line_term(self, line_term: typing.Optional[builtins.str], length: builtins.int) -> None: ...

    def shutdown(self, flush: builtins.bool) -> IOStatus: ...

    def unix_get_fd(self) -> builtins.int: ...

    @staticmethod
    def unix_new(fd: builtins.int) -> IOChannel: ...

    def unref(self) -> None: ...

    def write(self, buf: builtins.str, count: builtins.int, bytes_written: builtins.int) -> IOError: ...

    def write_chars(self, buf: builtins.bytes, count: builtins.int) -> typing.Tuple[IOStatus, builtins.int]: ...

    def write_unichar(self, thechar: builtins.str) -> IOStatus: ...


class IOFuncs():
    io_close: builtins.object
    io_create_watch: builtins.object
    io_free: builtins.object
    io_get_flags: builtins.object
    io_read: builtins.object
    io_seek: builtins.object
    io_set_flags: builtins.object
    io_write: builtins.object


class Idle():

    def get_current_time(self, timeval: TimeVal) -> None: ...

    def set_callback(self, func: SourceFunc, *data: typing.Optional[builtins.object]) -> None: ...


class KeyFile():

    @staticmethod
    def error_quark() -> builtins.int: ...

    def get_boolean(self, group_name: builtins.str, key: builtins.str) -> builtins.bool: ...

    def get_boolean_list(self, group_name: builtins.str, key: builtins.str) -> typing.Sequence[builtins.bool]: ...

    def get_comment(self, group_name: typing.Optional[builtins.str], key: builtins.str) -> builtins.str: ...

    def get_double(self, group_name: builtins.str, key: builtins.str) -> builtins.float: ...

    def get_double_list(self, group_name: builtins.str, key: builtins.str) -> typing.Sequence[builtins.float]: ...

    def get_groups(self) -> typing.Tuple[typing.Sequence[builtins.str], builtins.int]: ...

    def get_int64(self, group_name: builtins.str, key: builtins.str) -> builtins.int: ...

    def get_integer(self, group_name: builtins.str, key: builtins.str) -> builtins.int: ...

    def get_integer_list(self, group_name: builtins.str, key: builtins.str) -> typing.Sequence[builtins.int]: ...

    def get_keys(self, group_name: builtins.str) -> typing.Tuple[typing.Sequence[builtins.str], builtins.int]: ...

    def get_locale_for_key(self, group_name: builtins.str, key: builtins.str, locale: typing.Optional[builtins.str]) -> typing.Optional[builtins.str]: ...

    def get_locale_string(self, group_name: builtins.str, key: builtins.str, locale: typing.Optional[builtins.str]) -> builtins.str: ...

    def get_locale_string_list(self, group_name: builtins.str, key: builtins.str, locale: typing.Optional[builtins.str]) -> typing.Sequence[builtins.str]: ...

    def get_start_group(self) -> builtins.str: ...

    def get_string(self, group_name: builtins.str, key: builtins.str) -> builtins.str: ...

    def get_string_list(self, group_name: builtins.str, key: builtins.str) -> typing.Sequence[builtins.str]: ...

    def get_uint64(self, group_name: builtins.str, key: builtins.str) -> builtins.int: ...

    def get_value(self, group_name: builtins.str, key: builtins.str) -> builtins.str: ...

    def has_group(self, group_name: builtins.str) -> builtins.bool: ...

    def load_from_bytes(self, bytes: Bytes, flags: KeyFileFlags) -> builtins.bool: ...

    def load_from_data(self, data: builtins.str, length: builtins.int, flags: KeyFileFlags) -> builtins.bool: ...

    def load_from_data_dirs(self, file: builtins.str, flags: KeyFileFlags) -> typing.Tuple[builtins.bool, builtins.str]: ...

    def load_from_dirs(self, file: builtins.str, search_dirs: typing.Sequence[builtins.str], flags: KeyFileFlags) -> typing.Tuple[builtins.bool, builtins.str]: ...

    def load_from_file(self, file: builtins.str, flags: KeyFileFlags) -> builtins.bool: ...

    @staticmethod
    def new() -> KeyFile: ...

    def remove_comment(self, group_name: typing.Optional[builtins.str], key: typing.Optional[builtins.str]) -> builtins.bool: ...

    def remove_group(self, group_name: builtins.str) -> builtins.bool: ...

    def remove_key(self, group_name: builtins.str, key: builtins.str) -> builtins.bool: ...

    def save_to_file(self, filename: builtins.str) -> builtins.bool: ...

    def set_boolean(self, group_name: builtins.str, key: builtins.str, value: builtins.bool) -> None: ...

    def set_boolean_list(self, group_name: builtins.str, key: builtins.str, list: typing.Sequence[builtins.bool]) -> None: ...

    def set_comment(self, group_name: typing.Optional[builtins.str], key: typing.Optional[builtins.str], comment: builtins.str) -> builtins.bool: ...

    def set_double(self, group_name: builtins.str, key: builtins.str, value: builtins.float) -> None: ...

    def set_double_list(self, group_name: builtins.str, key: builtins.str, list: typing.Sequence[builtins.float]) -> None: ...

    def set_int64(self, group_name: builtins.str, key: builtins.str, value: builtins.int) -> None: ...

    def set_integer(self, group_name: builtins.str, key: builtins.str, value: builtins.int) -> None: ...

    def set_integer_list(self, group_name: builtins.str, key: builtins.str, list: typing.Sequence[builtins.int]) -> None: ...

    def set_list_separator(self, separator: builtins.int) -> None: ...

    def set_locale_string(self, group_name: builtins.str, key: builtins.str, locale: builtins.str, string: builtins.str) -> None: ...

    def set_locale_string_list(self, group_name: builtins.str, key: builtins.str, locale: builtins.str, list: typing.Sequence[builtins.str]) -> None: ...

    def set_string(self, group_name: builtins.str, key: builtins.str, string: builtins.str) -> None: ...

    def set_string_list(self, group_name: builtins.str, key: builtins.str, list: typing.Sequence[builtins.str]) -> None: ...

    def set_uint64(self, group_name: builtins.str, key: builtins.str, value: builtins.int) -> None: ...

    def set_value(self, group_name: builtins.str, key: builtins.str, value: builtins.str) -> None: ...

    def to_data(self) -> typing.Tuple[builtins.str, builtins.int]: ...

    def unref(self) -> None: ...


class List():
    data: builtins.object
    next: typing.Sequence[builtins.object]
    prev: typing.Sequence[builtins.object]


class LogField():
    key: builtins.str
    length: builtins.int
    value: builtins.object


class MainContext():

    def acquire(self) -> builtins.bool: ...

    def add_poll(self, fd: PollFD, priority: builtins.int) -> None: ...

    def check(self, max_priority: builtins.int, fds: typing.Sequence[PollFD]) -> builtins.bool: ...

    @staticmethod
    def default() -> MainContext: ...

    def dispatch(self) -> None: ...

    def find_source_by_funcs_user_data(self, funcs: SourceFuncs, user_data: typing.Optional[builtins.object]) -> Source: ...

    def find_source_by_id(self, source_id: builtins.int) -> Source: ...

    def find_source_by_user_data(self, user_data: typing.Optional[builtins.object]) -> Source: ...

    @staticmethod
    def get_thread_default() -> MainContext: ...

    def invoke_full(self, priority: builtins.int, function: SourceFunc, *data: typing.Optional[builtins.object]) -> None: ...

    def is_owner(self) -> builtins.bool: ...

    def iteration(self, may_block: builtins.bool) -> builtins.bool: ...

    @staticmethod
    def new() -> MainContext: ...

    def pending(self) -> builtins.bool: ...

    def pop_thread_default(self) -> None: ...

    def prepare(self) -> typing.Tuple[builtins.bool, builtins.int]: ...

    def push_thread_default(self) -> None: ...

    def query(self, max_priority: builtins.int) -> typing.Tuple[builtins.int, builtins.int, typing.Sequence[PollFD]]: ...

    def ref(self) -> MainContext: ...

    @staticmethod
    def ref_thread_default() -> MainContext: ...

    def release(self) -> None: ...

    def remove_poll(self, fd: PollFD) -> None: ...

    def unref(self) -> None: ...

    def wait(self, cond: Cond, mutex: Mutex) -> builtins.bool: ...

    def wakeup(self) -> None: ...


class MainLoop():

    def get_context(self) -> MainContext: ...

    def is_running(self) -> builtins.bool: ...

    @staticmethod
    def new(context: typing.Optional[MainContext], is_running: builtins.bool) -> MainLoop: ...

    def quit(self) -> None: ...

    def ref(self) -> MainLoop: ...

    def run(self) -> None: ...

    def unref(self) -> None: ...


class MappedFile():

    def free(self) -> None: ...

    def get_bytes(self) -> Bytes: ...

    def get_contents(self) -> builtins.str: ...

    def get_length(self) -> builtins.int: ...

    @staticmethod
    def new(filename: builtins.str, writable: builtins.bool) -> MappedFile: ...

    @staticmethod
    def new_from_fd(fd: builtins.int, writable: builtins.bool) -> MappedFile: ...

    def ref(self) -> MappedFile: ...

    def unref(self) -> None: ...


class MarkupParseContext():

    def end_parse(self) -> builtins.bool: ...

    def free(self) -> None: ...

    def get_element(self) -> builtins.str: ...

    def get_position(self) -> typing.Tuple[builtins.int, builtins.int]: ...

    def get_user_data(self) -> typing.Optional[builtins.object]: ...

    @staticmethod
    def new(parser: MarkupParser, flags: MarkupParseFlags, user_data: typing.Optional[builtins.object], user_data_dnotify: DestroyNotify) -> MarkupParseContext: ...

    def parse(self, text: builtins.str, text_len: builtins.int) -> builtins.bool: ...

    def pop(self) -> typing.Optional[builtins.object]: ...

    def push(self, parser: MarkupParser, user_data: typing.Optional[builtins.object]) -> None: ...

    def ref(self) -> MarkupParseContext: ...

    def unref(self) -> None: ...


class MarkupParser():
    end_element: builtins.object
    error: builtins.object
    passthrough: builtins.object
    start_element: builtins.object
    text: builtins.object


class MatchInfo():

    def expand_references(self, string_to_expand: builtins.str) -> typing.Optional[builtins.str]: ...

    def fetch(self, match_num: builtins.int) -> typing.Optional[builtins.str]: ...

    def fetch_all(self) -> typing.Sequence[builtins.str]: ...

    def fetch_named(self, name: builtins.str) -> typing.Optional[builtins.str]: ...

    def fetch_named_pos(self, name: builtins.str) -> typing.Tuple[builtins.bool, builtins.int, builtins.int]: ...

    def fetch_pos(self, match_num: builtins.int) -> typing.Tuple[builtins.bool, builtins.int, builtins.int]: ...

    def free(self) -> None: ...

    def get_match_count(self) -> builtins.int: ...

    def get_regex(self) -> Regex: ...

    def get_string(self) -> builtins.str: ...

    def is_partial_match(self) -> builtins.bool: ...

    def matches(self) -> builtins.bool: ...

    def next(self) -> builtins.bool: ...

    def ref(self) -> MatchInfo: ...

    def unref(self) -> None: ...


class MemVTable():
    calloc: builtins.object
    free: builtins.object
    malloc: builtins.object
    realloc: builtins.object
    try_malloc: builtins.object
    try_realloc: builtins.object


class Node():
    children: Node
    data: builtins.object
    next: Node
    parent: Node
    prev: Node

    def child_index(self, data: typing.Optional[builtins.object]) -> builtins.int: ...

    def child_position(self, child: Node) -> builtins.int: ...

    def depth(self) -> builtins.int: ...

    def destroy(self) -> None: ...

    def is_ancestor(self, descendant: Node) -> builtins.bool: ...

    def max_height(self) -> builtins.int: ...

    def n_children(self) -> builtins.int: ...

    def n_nodes(self, flags: TraverseFlags) -> builtins.int: ...

    def reverse_children(self) -> None: ...

    def unlink(self) -> None: ...


class Once():
    retval: builtins.object
    status: OnceStatus

    @staticmethod
    def init_enter(location: builtins.object) -> builtins.bool: ...

    @staticmethod
    def init_leave(location: builtins.object, result: builtins.int) -> None: ...


class OptionContext():

    def add_group(self, group: OptionGroup) -> None: ...

    def add_main_entries(self, entries: typing.Sequence[OptionEntry], translation_domain: typing.Optional[builtins.str]) -> None: ...

    def free(self) -> None: ...

    def get_description(self) -> builtins.str: ...

    def get_help(self, main_help: builtins.bool, group: typing.Optional[OptionGroup]) -> builtins.str: ...

    def get_help_enabled(self) -> builtins.bool: ...

    def get_ignore_unknown_options(self) -> builtins.bool: ...

    def get_main_group(self) -> OptionGroup: ...

    def get_strict_posix(self) -> builtins.bool: ...

    def get_summary(self) -> builtins.str: ...

    def parse(self, argv: typing.Sequence[builtins.str]) -> typing.Tuple[builtins.bool, typing.Sequence[builtins.str]]: ...

    def parse_strv(self, arguments: typing.Sequence[builtins.str]) -> typing.Tuple[builtins.bool, typing.Sequence[builtins.str]]: ...

    def set_description(self, description: typing.Optional[builtins.str]) -> None: ...

    def set_help_enabled(self, help_enabled: builtins.bool) -> None: ...

    def set_ignore_unknown_options(self, ignore_unknown: builtins.bool) -> None: ...

    def set_main_group(self, group: OptionGroup) -> None: ...

    def set_strict_posix(self, strict_posix: builtins.bool) -> None: ...

    def set_summary(self, summary: typing.Optional[builtins.str]) -> None: ...

    def set_translate_func(self, func: typing.Optional[TranslateFunc], *data: typing.Optional[builtins.object]) -> None: ...

    def set_translation_domain(self, domain: builtins.str) -> None: ...


class OptionEntry():
    arg: OptionArg
    arg_data: builtins.object
    arg_description: builtins.str
    description: builtins.str
    flags: builtins.int
    long_name: builtins.str
    short_name: builtins.int


class OptionGroup():

    def add_entries(self, entries: typing.Sequence[OptionEntry]) -> None: ...

    def free(self) -> None: ...

    @staticmethod
    def new(name: builtins.str, description: builtins.str, help_description: builtins.str, user_data: typing.Optional[builtins.object], destroy: typing.Optional[DestroyNotify]) -> OptionGroup: ...

    def ref(self) -> OptionGroup: ...

    def set_translate_func(self, func: typing.Optional[TranslateFunc], *data: typing.Optional[builtins.object]) -> None: ...

    def set_translation_domain(self, domain: builtins.str) -> None: ...

    def unref(self) -> None: ...


class PatternSpec():

    def equal(self, pspec2: PatternSpec) -> builtins.bool: ...

    def free(self) -> None: ...


class PollFD():
    events: builtins.int
    fd: builtins.int
    revents: builtins.int


class Private():
    future: typing.Sequence[builtins.object]
    notify: DestroyNotify
    p: builtins.object

    def get(self) -> typing.Optional[builtins.object]: ...

    def replace(self, value: typing.Optional[builtins.object]) -> None: ...

    def set(self, value: typing.Optional[builtins.object]) -> None: ...


class PtrArray():
    len: builtins.int
    pdata: builtins.object


class Queue():
    head: typing.Sequence[builtins.object]
    length: builtins.int
    tail: typing.Sequence[builtins.object]

    def clear(self) -> None: ...

    def clear_full(self, free_func: typing.Optional[DestroyNotify]) -> None: ...

    def free(self) -> None: ...

    def free_full(self, free_func: DestroyNotify) -> None: ...

    def get_length(self) -> builtins.int: ...

    def index(self, data: typing.Optional[builtins.object]) -> builtins.int: ...

    def init(self) -> None: ...

    def is_empty(self) -> builtins.bool: ...

    def peek_head(self) -> typing.Optional[builtins.object]: ...

    def peek_nth(self, n: builtins.int) -> typing.Optional[builtins.object]: ...

    def peek_tail(self) -> typing.Optional[builtins.object]: ...

    def pop_head(self) -> typing.Optional[builtins.object]: ...

    def pop_nth(self, n: builtins.int) -> typing.Optional[builtins.object]: ...

    def pop_tail(self) -> typing.Optional[builtins.object]: ...

    def push_head(self, data: typing.Optional[builtins.object]) -> None: ...

    def push_nth(self, data: typing.Optional[builtins.object], n: builtins.int) -> None: ...

    def push_tail(self, data: typing.Optional[builtins.object]) -> None: ...

    def remove(self, data: typing.Optional[builtins.object]) -> builtins.bool: ...

    def remove_all(self, data: typing.Optional[builtins.object]) -> builtins.int: ...

    def reverse(self) -> None: ...


class RWLock():
    i: typing.Sequence[builtins.int]
    p: builtins.object

    def clear(self) -> None: ...

    def init(self) -> None: ...

    def reader_lock(self) -> None: ...

    def reader_trylock(self) -> builtins.bool: ...

    def reader_unlock(self) -> None: ...

    def writer_lock(self) -> None: ...

    def writer_trylock(self) -> builtins.bool: ...

    def writer_unlock(self) -> None: ...


class Rand():

    def double(self) -> builtins.float: ...

    def double_range(self, begin: builtins.float, end: builtins.float) -> builtins.float: ...

    def free(self) -> None: ...

    def int(self) -> builtins.int: ...

    def int_range(self, begin: builtins.int, end: builtins.int) -> builtins.int: ...

    def set_seed(self, seed: builtins.int) -> None: ...

    def set_seed_array(self, seed: builtins.int, seed_length: builtins.int) -> None: ...


class RecMutex():
    i: typing.Sequence[builtins.int]
    p: builtins.object

    def clear(self) -> None: ...

    def init(self) -> None: ...

    def lock(self) -> None: ...

    def trylock(self) -> builtins.bool: ...

    def unlock(self) -> None: ...


class Regex():

    @staticmethod
    def check_replacement(replacement: builtins.str) -> typing.Tuple[builtins.bool, builtins.bool]: ...

    @staticmethod
    def error_quark() -> builtins.int: ...

    @staticmethod
    def escape_nul(string: builtins.str, length: builtins.int) -> builtins.str: ...

    @staticmethod
    def escape_string(string: typing.Sequence[builtins.str]) -> builtins.str: ...

    def get_capture_count(self) -> builtins.int: ...

    def get_compile_flags(self) -> RegexCompileFlags: ...

    def get_has_cr_or_lf(self) -> builtins.bool: ...

    def get_match_flags(self) -> RegexMatchFlags: ...

    def get_max_backref(self) -> builtins.int: ...

    def get_max_lookbehind(self) -> builtins.int: ...

    def get_pattern(self) -> builtins.str: ...

    def get_string_number(self, name: builtins.str) -> builtins.int: ...

    def match(self, string: builtins.str, match_options: RegexMatchFlags) -> typing.Tuple[builtins.bool, MatchInfo]: ...

    def match_all(self, string: builtins.str, match_options: RegexMatchFlags) -> typing.Tuple[builtins.bool, MatchInfo]: ...

    def match_all_full(self, string: typing.Sequence[builtins.str], start_position: builtins.int, match_options: RegexMatchFlags) -> typing.Tuple[builtins.bool, MatchInfo]: ...

    def match_full(self, string: typing.Sequence[builtins.str], start_position: builtins.int, match_options: RegexMatchFlags) -> typing.Tuple[builtins.bool, MatchInfo]: ...

    @staticmethod
    def match_simple(pattern: builtins.str, string: builtins.str, compile_options: RegexCompileFlags, match_options: RegexMatchFlags) -> builtins.bool: ...

    @staticmethod
    def new(pattern: builtins.str, compile_options: RegexCompileFlags, match_options: RegexMatchFlags) -> typing.Optional[Regex]: ...

    def ref(self) -> Regex: ...

    def replace(self, string: typing.Sequence[builtins.str], start_position: builtins.int, replacement: builtins.str, match_options: RegexMatchFlags) -> builtins.str: ...

    def replace_literal(self, string: typing.Sequence[builtins.str], start_position: builtins.int, replacement: builtins.str, match_options: RegexMatchFlags) -> builtins.str: ...

    def split(self, string: builtins.str, match_options: RegexMatchFlags) -> typing.Sequence[builtins.str]: ...

    def split_full(self, string: typing.Sequence[builtins.str], start_position: builtins.int, match_options: RegexMatchFlags, max_tokens: builtins.int) -> typing.Sequence[builtins.str]: ...

    @staticmethod
    def split_simple(pattern: builtins.str, string: builtins.str, compile_options: RegexCompileFlags, match_options: RegexMatchFlags) -> typing.Sequence[builtins.str]: ...

    def unref(self) -> None: ...


class SList():
    data: builtins.object
    next: typing.Sequence[builtins.object]


class Scanner():
    buffer: builtins.str
    config: ScannerConfig
    input_fd: builtins.int
    input_name: builtins.str
    line: builtins.int
    max_parse_errors: builtins.int
    msg_handler: ScannerMsgFunc
    next_line: builtins.int
    next_position: builtins.int
    next_token: TokenType
    next_value: TokenValue
    parse_errors: builtins.int
    position: builtins.int
    qdata: Data
    scope_id: builtins.int
    symbol_table: typing.Mapping[builtins.object, builtins.object]
    text: builtins.str
    text_end: builtins.str
    token: TokenType
    user_data: builtins.object
    value: TokenValue

    def cur_line(self) -> builtins.int: ...

    def cur_position(self) -> builtins.int: ...

    def cur_token(self) -> TokenType: ...

    def destroy(self) -> None: ...

    def eof(self) -> builtins.bool: ...

    def get_next_token(self) -> TokenType: ...

    def input_file(self, input_fd: builtins.int) -> None: ...

    def input_text(self, text: builtins.str, text_len: builtins.int) -> None: ...

    def lookup_symbol(self, symbol: builtins.str) -> typing.Optional[builtins.object]: ...

    def peek_next_token(self) -> TokenType: ...

    def scope_add_symbol(self, scope_id: builtins.int, symbol: builtins.str, value: typing.Optional[builtins.object]) -> None: ...

    def scope_lookup_symbol(self, scope_id: builtins.int, symbol: builtins.str) -> typing.Optional[builtins.object]: ...

    def scope_remove_symbol(self, scope_id: builtins.int, symbol: builtins.str) -> None: ...

    def set_scope(self, scope_id: builtins.int) -> builtins.int: ...

    def sync_file_offset(self) -> None: ...

    def unexp_token(self, expected_token: TokenType, identifier_spec: builtins.str, symbol_spec: builtins.str, symbol_name: builtins.str, message: builtins.str, is_error: builtins.int) -> None: ...


class ScannerConfig():
    case_sensitive: builtins.int
    char_2_token: builtins.int
    cpair_comment_single: builtins.str
    cset_identifier_first: builtins.str
    cset_identifier_nth: builtins.str
    cset_skip_characters: builtins.str
    identifier_2_string: builtins.int
    int_2_float: builtins.int
    numbers_2_int: builtins.int
    padding_dummy: builtins.int
    scan_binary: builtins.int
    scan_comment_multi: builtins.int
    scan_float: builtins.int
    scan_hex: builtins.int
    scan_hex_dollar: builtins.int
    scan_identifier: builtins.int
    scan_identifier_1char: builtins.int
    scan_identifier_NULL: builtins.int
    scan_octal: builtins.int
    scan_string_dq: builtins.int
    scan_string_sq: builtins.int
    scan_symbols: builtins.int
    scope_0_fallback: builtins.int
    skip_comment_multi: builtins.int
    skip_comment_single: builtins.int
    store_int64: builtins.int
    symbol_2_token: builtins.int


class Sequence():

    def append(self, data: typing.Optional[builtins.object]) -> SequenceIter: ...

    def free(self) -> None: ...

    @staticmethod
    def get(iter: SequenceIter) -> typing.Optional[builtins.object]: ...

    def get_begin_iter(self) -> SequenceIter: ...

    def get_end_iter(self) -> SequenceIter: ...

    def get_iter_at_pos(self, pos: builtins.int) -> SequenceIter: ...

    def get_length(self) -> builtins.int: ...

    @staticmethod
    def insert_before(iter: SequenceIter, data: typing.Optional[builtins.object]) -> SequenceIter: ...

    def is_empty(self) -> builtins.bool: ...

    @staticmethod
    def move(src: SequenceIter, dest: SequenceIter) -> None: ...

    @staticmethod
    def move_range(dest: SequenceIter, begin: SequenceIter, end: SequenceIter) -> None: ...

    def prepend(self, data: typing.Optional[builtins.object]) -> SequenceIter: ...

    @staticmethod
    def range_get_midpoint(begin: SequenceIter, end: SequenceIter) -> SequenceIter: ...

    @staticmethod
    def remove(iter: SequenceIter) -> None: ...

    @staticmethod
    def remove_range(begin: SequenceIter, end: SequenceIter) -> None: ...

    @staticmethod
    def set(iter: SequenceIter, data: typing.Optional[builtins.object]) -> None: ...

    @staticmethod
    def swap(a: SequenceIter, b: SequenceIter) -> None: ...


class SequenceIter():

    def compare(self, b: SequenceIter) -> builtins.int: ...

    def get_position(self) -> builtins.int: ...

    def get_sequence(self) -> Sequence: ...

    def is_begin(self) -> builtins.bool: ...

    def is_end(self) -> builtins.bool: ...

    def move(self, delta: builtins.int) -> SequenceIter: ...

    def next(self) -> SequenceIter: ...

    def prev(self) -> SequenceIter: ...


class Source():
    callback_data: builtins.object
    callback_funcs: SourceCallbackFuncs
    context: MainContext
    flags: builtins.int
    name: builtins.str
    next: Source
    poll_fds: typing.Sequence[builtins.object]
    prev: Source
    ref_count: builtins.int
    source_funcs: SourceFuncs
    source_id: builtins.int

    def add_child_source(self, child_source: Source) -> None: ...

    def add_poll(self, fd: PollFD) -> None: ...

    def add_unix_fd(self, fd: builtins.int, events: IOCondition) -> builtins.object: ...

    def attach(self, context: typing.Optional[MainContext]) -> builtins.int: ...

    def destroy(self) -> None: ...

    def get_can_recurse(self) -> builtins.bool: ...

    def get_context(self) -> typing.Optional[MainContext]: ...

    def get_current_time(self, timeval: TimeVal) -> None: ...

    def get_id(self) -> builtins.int: ...

    def get_name(self) -> builtins.str: ...

    def get_priority(self) -> builtins.int: ...

    def get_ready_time(self) -> builtins.int: ...

    def get_time(self) -> builtins.int: ...

    def is_destroyed(self) -> builtins.bool: ...

    def modify_unix_fd(self, tag: builtins.object, new_events: IOCondition) -> None: ...

    @staticmethod
    def new(source_funcs: SourceFuncs, struct_size: builtins.int) -> Source: ...

    def query_unix_fd(self, tag: builtins.object) -> IOCondition: ...

    def ref(self) -> Source: ...

    @staticmethod
    def remove(tag: builtins.int) -> builtins.bool: ...

    @staticmethod
    def remove_by_funcs_user_data(funcs: SourceFuncs, user_data: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def remove_by_user_data(user_data: typing.Optional[builtins.object]) -> builtins.bool: ...

    def remove_child_source(self, child_source: Source) -> None: ...

    def remove_poll(self, fd: PollFD) -> None: ...

    def remove_unix_fd(self, tag: builtins.object) -> None: ...

    def set_callback(self, func: SourceFunc, *data: typing.Optional[builtins.object]) -> None: ...

    def set_callback_indirect(self, callback_data: typing.Optional[builtins.object], callback_funcs: SourceCallbackFuncs) -> None: ...

    def set_can_recurse(self, can_recurse: builtins.bool) -> None: ...

    def set_funcs(self, funcs: SourceFuncs) -> None: ...

    def set_name(self, name: builtins.str) -> None: ...

    @staticmethod
    def set_name_by_id(tag: builtins.int, name: builtins.str) -> None: ...

    def set_priority(self, priority: builtins.int) -> None: ...

    def set_ready_time(self, ready_time: builtins.int) -> None: ...

    def unref(self) -> None: ...


class SourceCallbackFuncs():
    get: builtins.object
    ref: builtins.object
    unref: builtins.object


class SourceFuncs():
    check: builtins.object
    closure_callback: SourceFunc
    closure_marshal: SourceDummyMarshal
    dispatch: builtins.object
    finalize: builtins.object
    prepare: builtins.object


class StatBuf():
    ...


class String():
    allocated_len: builtins.int
    len: builtins.int
    str: builtins.str

    def append(self, val: builtins.str) -> String: ...

    def append_c(self, c: builtins.int) -> String: ...

    def append_len(self, val: builtins.str, len: builtins.int) -> String: ...

    def append_unichar(self, wc: builtins.str) -> String: ...

    def append_uri_escaped(self, unescaped: builtins.str, reserved_chars_allowed: builtins.str, allow_utf8: builtins.bool) -> String: ...

    def ascii_down(self) -> String: ...

    def ascii_up(self) -> String: ...

    def assign(self, rval: builtins.str) -> String: ...

    def down(self) -> String: ...

    def equal(self, v2: String) -> builtins.bool: ...

    def erase(self, pos: builtins.int, len: builtins.int) -> String: ...

    def free(self, free_segment: builtins.bool) -> typing.Optional[builtins.str]: ...

    def free_to_bytes(self) -> Bytes: ...

    def hash(self) -> builtins.int: ...

    def insert(self, pos: builtins.int, val: builtins.str) -> String: ...

    def insert_c(self, pos: builtins.int, c: builtins.int) -> String: ...

    def insert_len(self, pos: builtins.int, val: builtins.str, len: builtins.int) -> String: ...

    def insert_unichar(self, pos: builtins.int, wc: builtins.str) -> String: ...

    def overwrite(self, pos: builtins.int, val: builtins.str) -> String: ...

    def overwrite_len(self, pos: builtins.int, val: builtins.str, len: builtins.int) -> String: ...

    def prepend(self, val: builtins.str) -> String: ...

    def prepend_c(self, c: builtins.int) -> String: ...

    def prepend_len(self, val: builtins.str, len: builtins.int) -> String: ...

    def prepend_unichar(self, wc: builtins.str) -> String: ...

    def set_size(self, len: builtins.int) -> String: ...

    def truncate(self, len: builtins.int) -> String: ...

    def up(self) -> String: ...


class StringChunk():

    def clear(self) -> None: ...

    def free(self) -> None: ...

    def insert(self, string: builtins.str) -> builtins.str: ...

    def insert_const(self, string: builtins.str) -> builtins.str: ...

    def insert_len(self, string: builtins.str, len: builtins.int) -> builtins.str: ...


class TestCase():
    ...


class TestConfig():
    test_initialized: builtins.bool
    test_perf: builtins.bool
    test_quick: builtins.bool
    test_quiet: builtins.bool
    test_undefined: builtins.bool
    test_verbose: builtins.bool


class TestLogBuffer():
    data: String
    msgs: typing.Sequence[builtins.object]

    def free(self) -> None: ...

    def push(self, n_bytes: builtins.int, bytes: builtins.int) -> None: ...


class TestLogMsg():
    log_type: TestLogType
    n_nums: builtins.int
    n_strings: builtins.int
    nums: builtins.object
    strings: builtins.str

    def free(self) -> None: ...


class TestSuite():

    def add(self, test_case: TestCase) -> None: ...

    def add_suite(self, nestedsuite: TestSuite) -> None: ...


class Thread():

    @staticmethod
    def error_quark() -> builtins.int: ...

    @staticmethod
    def exit(retval: typing.Optional[builtins.object]) -> None: ...

    def join(self) -> typing.Optional[builtins.object]: ...

    def ref(self) -> Thread: ...

    @staticmethod
    def self() -> Thread: ...

    def unref(self) -> None: ...

    @staticmethod
    def yield_() -> None: ...


class ThreadPool():
    exclusive: builtins.bool
    func: Func
    user_data: builtins.object

    def free(self, immediate: builtins.bool, wait_: builtins.bool) -> None: ...

    @staticmethod
    def get_max_idle_time() -> builtins.int: ...

    def get_max_threads(self) -> builtins.int: ...

    @staticmethod
    def get_max_unused_threads() -> builtins.int: ...

    def get_num_threads(self) -> builtins.int: ...

    @staticmethod
    def get_num_unused_threads() -> builtins.int: ...

    def move_to_front(self, data: typing.Optional[builtins.object]) -> builtins.bool: ...

    def push(self, data: typing.Optional[builtins.object]) -> builtins.bool: ...

    @staticmethod
    def set_max_idle_time(interval: builtins.int) -> None: ...

    def set_max_threads(self, max_threads: builtins.int) -> builtins.bool: ...

    @staticmethod
    def set_max_unused_threads(max_threads: builtins.int) -> None: ...

    @staticmethod
    def stop_unused_threads() -> None: ...

    def unprocessed(self) -> builtins.int: ...


class TimeVal():
    tv_sec: builtins.int
    tv_usec: builtins.int

    def add(self, microseconds: builtins.int) -> None: ...

    @staticmethod
    def from_iso8601(iso_date: builtins.str) -> typing.Tuple[builtins.bool, TimeVal]: ...

    def to_iso8601(self) -> typing.Optional[builtins.str]: ...


class TimeZone():

    def adjust_time(self, type: TimeType, time_: builtins.int) -> builtins.int: ...

    def find_interval(self, type: TimeType, time_: builtins.int) -> builtins.int: ...

    def get_abbreviation(self, interval: builtins.int) -> builtins.str: ...

    def get_identifier(self) -> builtins.str: ...

    def get_offset(self, interval: builtins.int) -> builtins.int: ...

    def is_dst(self, interval: builtins.int) -> builtins.bool: ...

    @staticmethod
    def new(identifier: typing.Optional[builtins.str]) -> TimeZone: ...

    @staticmethod
    def new_local() -> TimeZone: ...

    @staticmethod
    def new_offset(seconds: builtins.int) -> TimeZone: ...

    @staticmethod
    def new_utc() -> TimeZone: ...

    def ref(self) -> TimeZone: ...

    def unref(self) -> None: ...


class Timeout():

    def get_current_time(self, timeval: TimeVal) -> None: ...

    def set_callback(self, func: SourceFunc, *data: typing.Optional[builtins.object]) -> None: ...


class Timer():

    def continue_(self) -> None: ...

    def destroy(self) -> None: ...

    def elapsed(self, microseconds: builtins.int) -> builtins.float: ...

    def is_active(self) -> builtins.bool: ...

    def reset(self) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...


class TrashStack():
    next: TrashStack

    @staticmethod
    def height(stack_p: TrashStack) -> builtins.int: ...

    @staticmethod
    def peek(stack_p: TrashStack) -> typing.Optional[builtins.object]: ...

    @staticmethod
    def pop(stack_p: TrashStack) -> typing.Optional[builtins.object]: ...

    @staticmethod
    def push(stack_p: TrashStack, data_p: builtins.object) -> None: ...


class Tree():

    def destroy(self) -> None: ...

    def height(self) -> builtins.int: ...

    def insert(self, key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> None: ...

    def lookup(self, key: typing.Optional[builtins.object]) -> typing.Optional[builtins.object]: ...

    def lookup_extended(self, lookup_key: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...

    def nnodes(self) -> builtins.int: ...

    def remove(self, key: typing.Optional[builtins.object]) -> builtins.bool: ...

    def replace(self, key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> None: ...

    def steal(self, key: typing.Optional[builtins.object]) -> builtins.bool: ...

    def unref(self) -> None: ...


class Variant():
    def __new__(cls, format_string: str, value: object) -> Variant: ...

    def byteswap(self) -> Variant: ...

    def check_format_string(self, format_string: builtins.str, copy_only: builtins.bool) -> builtins.bool: ...

    def classify(self) -> VariantClass: ...

    def compare(self, two: Variant) -> builtins.int: ...

    def dup_bytestring(self) -> builtins.bytes: ...

    def dup_bytestring_array(self) -> typing.Sequence[builtins.str]: ...

    def dup_objv(self) -> typing.Sequence[builtins.str]: ...

    def dup_string(self) -> typing.Tuple[builtins.str, builtins.int]: ...

    def dup_strv(self) -> typing.Sequence[builtins.str]: ...

    def equal(self, two: Variant) -> builtins.bool: ...

    def get_boolean(self) -> builtins.bool: ...

    def get_byte(self) -> builtins.int: ...

    def get_bytestring(self) -> builtins.bytes: ...

    def get_bytestring_array(self) -> typing.Sequence[builtins.str]: ...

    def get_child_value(self, index_: builtins.int) -> Variant: ...

    def get_data(self) -> typing.Optional[builtins.object]: ...

    def get_data_as_bytes(self) -> Bytes: ...

    def get_double(self) -> builtins.float: ...

    def get_handle(self) -> builtins.int: ...

    def get_int16(self) -> builtins.int: ...

    def get_int32(self) -> builtins.int: ...

    def get_int64(self) -> builtins.int: ...

    def get_maybe(self) -> typing.Optional[Variant]: ...

    def get_normal_form(self) -> Variant: ...

    def get_objv(self) -> typing.Sequence[builtins.str]: ...

    def get_size(self) -> builtins.int: ...

    def get_string(self) -> typing.Tuple[builtins.str, builtins.int]: ...

    def get_strv(self) -> typing.Sequence[builtins.str]: ...

    def get_type(self) -> VariantType: ...

    def get_type_string(self) -> builtins.str: ...

    def get_uint16(self) -> builtins.int: ...

    def get_uint32(self) -> builtins.int: ...

    def get_uint64(self) -> builtins.int: ...

    def get_variant(self) -> Variant: ...

    def hash(self) -> builtins.int: ...

    def is_container(self) -> builtins.bool: ...

    def is_floating(self) -> builtins.bool: ...

    def is_normal_form(self) -> builtins.bool: ...

    @staticmethod
    def is_object_path(string: builtins.str) -> builtins.bool: ...

    def is_of_type(self, type: VariantType) -> builtins.bool: ...

    @staticmethod
    def is_signature(string: builtins.str) -> builtins.bool: ...

    def lookup_value(self, key: builtins.str, expected_type: typing.Optional[VariantType]) -> Variant: ...

    def n_children(self) -> builtins.int: ...

    @staticmethod
    def new_array(child_type: typing.Optional[VariantType], children: typing.Optional[typing.Sequence[Variant]]) -> Variant: ...

    @staticmethod
    def new_boolean(value: builtins.bool) -> Variant: ...

    @staticmethod
    def new_byte(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_bytestring(string: builtins.bytes) -> Variant: ...

    @staticmethod
    def new_bytestring_array(strv: typing.Sequence[builtins.str]) -> Variant: ...

    @staticmethod
    def new_dict_entry(key: Variant, value: Variant) -> Variant: ...

    @staticmethod
    def new_double(value: builtins.float) -> Variant: ...

    @staticmethod
    def new_fixed_array(element_type: VariantType, elements: typing.Optional[builtins.object], n_elements: builtins.int, element_size: builtins.int) -> Variant: ...

    @staticmethod
    def new_from_bytes(type: VariantType, bytes: Bytes, trusted: builtins.bool) -> Variant: ...

    @staticmethod
    def new_from_data(type: VariantType, data: builtins.bytes, trusted: builtins.bool, notify: DestroyNotify, user_data: typing.Optional[builtins.object]) -> Variant: ...

    @staticmethod
    def new_handle(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_int16(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_int32(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_int64(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_maybe(child_type: typing.Optional[VariantType], child: typing.Optional[Variant]) -> Variant: ...

    @staticmethod
    def new_object_path(object_path: builtins.str) -> Variant: ...

    @staticmethod
    def new_objv(strv: typing.Sequence[builtins.str]) -> Variant: ...

    @staticmethod
    def new_signature(signature: builtins.str) -> Variant: ...

    @staticmethod
    def new_string(string: builtins.str) -> Variant: ...

    @staticmethod
    def new_strv(strv: typing.Sequence[builtins.str]) -> Variant: ...

    @staticmethod
    def new_tuple(children: typing.Sequence[Variant]) -> Variant: ...

    @staticmethod
    def new_uint16(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_uint32(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_uint64(value: builtins.int) -> Variant: ...

    @staticmethod
    def new_variant(value: Variant) -> Variant: ...

    @staticmethod
    def parse(type: typing.Optional[VariantType], text: builtins.str, limit: typing.Optional[builtins.str], endptr: typing.Optional[builtins.str]) -> Variant: ...

    @staticmethod
    def parse_error_print_context(error: Error, source_str: builtins.str) -> builtins.str: ...

    @staticmethod
    def parse_error_quark() -> builtins.int: ...

    @staticmethod
    def parser_get_error_quark() -> builtins.int: ...

    def print_(self, type_annotate: builtins.bool) -> builtins.str: ...

    def ref(self) -> Variant: ...

    def ref_sink(self) -> Variant: ...

    def store(self, data: builtins.object) -> None: ...

    def take_ref(self) -> Variant: ...

    def unpack(self) -> typing.Any: ...

    def unref(self) -> None: ...


class VariantBuilder():

    def add_value(self, value: Variant) -> None: ...

    def close(self) -> None: ...

    def end(self) -> Variant: ...

    @staticmethod
    def new(type: VariantType) -> VariantBuilder: ...

    def open(self, type: VariantType) -> None: ...

    def ref(self) -> VariantBuilder: ...

    def unref(self) -> None: ...


class VariantDict():

    def clear(self) -> None: ...

    def contains(self, key: builtins.str) -> builtins.bool: ...

    def end(self) -> Variant: ...

    def insert_value(self, key: builtins.str, value: Variant) -> None: ...

    def lookup_value(self, key: builtins.str, expected_type: typing.Optional[VariantType]) -> Variant: ...

    @staticmethod
    def new(from_asv: typing.Optional[Variant]) -> VariantDict: ...

    def ref(self) -> VariantDict: ...

    def remove(self, key: builtins.str) -> builtins.bool: ...

    def unref(self) -> None: ...


class VariantType():

    @staticmethod
    def checked_(arg0: builtins.str) -> VariantType: ...

    def copy(self) -> VariantType: ...

    def dup_string(self) -> builtins.str: ...

    def element(self) -> VariantType: ...

    def equal(self, type2: VariantType) -> builtins.bool: ...

    def first(self) -> VariantType: ...

    def free(self) -> None: ...

    def get_string_length(self) -> builtins.int: ...

    def hash(self) -> builtins.int: ...

    def is_array(self) -> builtins.bool: ...

    def is_basic(self) -> builtins.bool: ...

    def is_container(self) -> builtins.bool: ...

    def is_definite(self) -> builtins.bool: ...

    def is_dict_entry(self) -> builtins.bool: ...

    def is_maybe(self) -> builtins.bool: ...

    def is_subtype_of(self, supertype: VariantType) -> builtins.bool: ...

    def is_tuple(self) -> builtins.bool: ...

    def is_variant(self) -> builtins.bool: ...

    def key(self) -> VariantType: ...

    def n_items(self) -> builtins.int: ...

    @staticmethod
    def new(type_string: builtins.str) -> VariantType: ...

    @staticmethod
    def new_array(element: VariantType) -> VariantType: ...

    @staticmethod
    def new_dict_entry(key: VariantType, value: VariantType) -> VariantType: ...

    @staticmethod
    def new_maybe(element: VariantType) -> VariantType: ...

    @staticmethod
    def new_tuple(items: typing.Sequence[VariantType]) -> VariantType: ...

    def next(self) -> VariantType: ...

    @staticmethod
    def string_get_depth_(type_string: builtins.str) -> builtins.int: ...

    @staticmethod
    def string_is_valid(type_string: builtins.str) -> builtins.bool: ...

    @staticmethod
    def string_scan(string: builtins.str, limit: typing.Optional[builtins.str]) -> typing.Tuple[builtins.bool, builtins.str]: ...

    def value(self) -> VariantType: ...


class DoubleIEEE754():
    v_double: builtins.float


class FloatIEEE754():
    v_float: builtins.float


class Mutex():
    i: typing.Sequence[builtins.int]
    p: builtins.object

    def clear(self) -> None: ...

    def init(self) -> None: ...

    def lock(self) -> None: ...

    def trylock(self) -> builtins.bool: ...

    def unlock(self) -> None: ...


class TokenValue():
    v_binary: builtins.int
    v_char: builtins.int
    v_comment: builtins.str
    v_error: builtins.int
    v_float: builtins.float
    v_hex: builtins.int
    v_identifier: builtins.str
    v_int64: builtins.int
    v_int: builtins.int
    v_octal: builtins.int
    v_string: builtins.str
    v_symbol: builtins.object


class AsciiType(Flags, builtins.int):
    ALNUM = ...  # type: AsciiType
    ALPHA = ...  # type: AsciiType
    CNTRL = ...  # type: AsciiType
    DIGIT = ...  # type: AsciiType
    GRAPH = ...  # type: AsciiType
    LOWER = ...  # type: AsciiType
    PRINT = ...  # type: AsciiType
    PUNCT = ...  # type: AsciiType
    SPACE = ...  # type: AsciiType
    UPPER = ...  # type: AsciiType
    XDIGIT = ...  # type: AsciiType


class FileTest(Flags, builtins.int):
    EXISTS = ...  # type: FileTest
    IS_DIR = ...  # type: FileTest
    IS_EXECUTABLE = ...  # type: FileTest
    IS_REGULAR = ...  # type: FileTest
    IS_SYMLINK = ...  # type: FileTest


class Flags(builtins.int):
    def __and__(self: FlagsT, other: typing.Union[int, FlagsT]) -> FlagsT: ...
    def __or__(self: FlagsT, other: typing.Union[int, FlagsT]) -> FlagsT: ...
    def __xor__(self: FlagsT, other: typing.Union[int, FlagsT]) -> FlagsT: ...


class FormatSizeFlags(Flags, builtins.int):
    BITS = ...  # type: FormatSizeFlags
    DEFAULT = ...  # type: FormatSizeFlags
    IEC_UNITS = ...  # type: FormatSizeFlags
    LONG_FORMAT = ...  # type: FormatSizeFlags


class HookFlagMask(Flags, builtins.int):
    ACTIVE = ...  # type: HookFlagMask
    IN_CALL = ...  # type: HookFlagMask
    MASK = ...  # type: HookFlagMask


class IOCondition(GObject.GFlags, builtins.int):
    ERR = ...  # type: IOCondition
    HUP = ...  # type: IOCondition
    IN = ...  # type: IOCondition
    NVAL = ...  # type: IOCondition
    OUT = ...  # type: IOCondition
    PRI = ...  # type: IOCondition


class IOFlags(Flags, builtins.int):
    APPEND = ...  # type: IOFlags
    GET_MASK = ...  # type: IOFlags
    IS_READABLE = ...  # type: IOFlags
    IS_SEEKABLE = ...  # type: IOFlags
    IS_WRITABLE = ...  # type: IOFlags
    IS_WRITEABLE = ...  # type: IOFlags
    MASK = ...  # type: IOFlags
    NONBLOCK = ...  # type: IOFlags
    SET_MASK = ...  # type: IOFlags


class KeyFileFlags(Flags, builtins.int):
    KEEP_COMMENTS = ...  # type: KeyFileFlags
    KEEP_TRANSLATIONS = ...  # type: KeyFileFlags
    NONE = ...  # type: KeyFileFlags


class LogLevelFlags(Flags, builtins.int):
    FLAG_FATAL = ...  # type: LogLevelFlags
    FLAG_RECURSION = ...  # type: LogLevelFlags
    LEVEL_CRITICAL = ...  # type: LogLevelFlags
    LEVEL_DEBUG = ...  # type: LogLevelFlags
    LEVEL_ERROR = ...  # type: LogLevelFlags
    LEVEL_INFO = ...  # type: LogLevelFlags
    LEVEL_MASK = ...  # type: LogLevelFlags
    LEVEL_MESSAGE = ...  # type: LogLevelFlags
    LEVEL_WARNING = ...  # type: LogLevelFlags


class MarkupCollectType(Flags, builtins.int):
    BOOLEAN = ...  # type: MarkupCollectType
    INVALID = ...  # type: MarkupCollectType
    OPTIONAL = ...  # type: MarkupCollectType
    STRDUP = ...  # type: MarkupCollectType
    STRING = ...  # type: MarkupCollectType
    TRISTATE = ...  # type: MarkupCollectType


class MarkupParseFlags(Flags, builtins.int):
    DO_NOT_USE_THIS_UNSUPPORTED_FLAG = ...  # type: MarkupParseFlags
    IGNORE_QUALIFIED = ...  # type: MarkupParseFlags
    PREFIX_ERROR_POSITION = ...  # type: MarkupParseFlags
    TREAT_CDATA_AS_TEXT = ...  # type: MarkupParseFlags


class OptionFlags(Flags, builtins.int):
    FILENAME = ...  # type: OptionFlags
    HIDDEN = ...  # type: OptionFlags
    IN_MAIN = ...  # type: OptionFlags
    NOALIAS = ...  # type: OptionFlags
    NONE = ...  # type: OptionFlags
    NO_ARG = ...  # type: OptionFlags
    OPTIONAL_ARG = ...  # type: OptionFlags
    REVERSE = ...  # type: OptionFlags


class RegexCompileFlags(Flags, builtins.int):
    ANCHORED = ...  # type: RegexCompileFlags
    BSR_ANYCRLF = ...  # type: RegexCompileFlags
    CASELESS = ...  # type: RegexCompileFlags
    DOLLAR_ENDONLY = ...  # type: RegexCompileFlags
    DOTALL = ...  # type: RegexCompileFlags
    DUPNAMES = ...  # type: RegexCompileFlags
    EXTENDED = ...  # type: RegexCompileFlags
    FIRSTLINE = ...  # type: RegexCompileFlags
    JAVASCRIPT_COMPAT = ...  # type: RegexCompileFlags
    MULTILINE = ...  # type: RegexCompileFlags
    NEWLINE_ANYCRLF = ...  # type: RegexCompileFlags
    NEWLINE_CR = ...  # type: RegexCompileFlags
    NEWLINE_CRLF = ...  # type: RegexCompileFlags
    NEWLINE_LF = ...  # type: RegexCompileFlags
    NO_AUTO_CAPTURE = ...  # type: RegexCompileFlags
    OPTIMIZE = ...  # type: RegexCompileFlags
    RAW = ...  # type: RegexCompileFlags
    UNGREEDY = ...  # type: RegexCompileFlags


class RegexMatchFlags(Flags, builtins.int):
    ANCHORED = ...  # type: RegexMatchFlags
    BSR_ANY = ...  # type: RegexMatchFlags
    BSR_ANYCRLF = ...  # type: RegexMatchFlags
    NEWLINE_ANY = ...  # type: RegexMatchFlags
    NEWLINE_ANYCRLF = ...  # type: RegexMatchFlags
    NEWLINE_CR = ...  # type: RegexMatchFlags
    NEWLINE_CRLF = ...  # type: RegexMatchFlags
    NEWLINE_LF = ...  # type: RegexMatchFlags
    NOTBOL = ...  # type: RegexMatchFlags
    NOTEMPTY = ...  # type: RegexMatchFlags
    NOTEMPTY_ATSTART = ...  # type: RegexMatchFlags
    NOTEOL = ...  # type: RegexMatchFlags
    PARTIAL = ...  # type: RegexMatchFlags
    PARTIAL_HARD = ...  # type: RegexMatchFlags
    PARTIAL_SOFT = ...  # type: RegexMatchFlags


class SpawnFlags(Flags, builtins.int):
    CHILD_INHERITS_STDIN = ...  # type: SpawnFlags
    CLOEXEC_PIPES = ...  # type: SpawnFlags
    DEFAULT = ...  # type: SpawnFlags
    DO_NOT_REAP_CHILD = ...  # type: SpawnFlags
    FILE_AND_ARGV_ZERO = ...  # type: SpawnFlags
    LEAVE_DESCRIPTORS_OPEN = ...  # type: SpawnFlags
    SEARCH_PATH = ...  # type: SpawnFlags
    SEARCH_PATH_FROM_ENVP = ...  # type: SpawnFlags
    STDERR_TO_DEV_NULL = ...  # type: SpawnFlags
    STDOUT_TO_DEV_NULL = ...  # type: SpawnFlags


class TestSubprocessFlags(Flags, builtins.int):
    STDERR = ...  # type: TestSubprocessFlags
    STDIN = ...  # type: TestSubprocessFlags
    STDOUT = ...  # type: TestSubprocessFlags


class TestTrapFlags(Flags, builtins.int):
    INHERIT_STDIN = ...  # type: TestTrapFlags
    SILENCE_STDERR = ...  # type: TestTrapFlags
    SILENCE_STDOUT = ...  # type: TestTrapFlags


class TraverseFlags(Flags, builtins.int):
    ALL = ...  # type: TraverseFlags
    LEAFS = ...  # type: TraverseFlags
    LEAVES = ...  # type: TraverseFlags
    MASK = ...  # type: TraverseFlags
    NON_LEAFS = ...  # type: TraverseFlags
    NON_LEAVES = ...  # type: TraverseFlags


class BookmarkFileError(Enum, builtins.int):
    APP_NOT_REGISTERED = ...  # type: BookmarkFileError
    FILE_NOT_FOUND = ...  # type: BookmarkFileError
    INVALID_URI = ...  # type: BookmarkFileError
    INVALID_VALUE = ...  # type: BookmarkFileError
    READ = ...  # type: BookmarkFileError
    UNKNOWN_ENCODING = ...  # type: BookmarkFileError
    URI_NOT_FOUND = ...  # type: BookmarkFileError
    WRITE = ...  # type: BookmarkFileError


class ChecksumType(Enum, builtins.int):
    MD5 = ...  # type: ChecksumType
    SHA1 = ...  # type: ChecksumType
    SHA256 = ...  # type: ChecksumType
    SHA384 = ...  # type: ChecksumType
    SHA512 = ...  # type: ChecksumType


class ConvertError(Enum, builtins.int):
    BAD_URI = ...  # type: ConvertError
    EMBEDDED_NUL = ...  # type: ConvertError
    FAILED = ...  # type: ConvertError
    ILLEGAL_SEQUENCE = ...  # type: ConvertError
    NOT_ABSOLUTE_PATH = ...  # type: ConvertError
    NO_CONVERSION = ...  # type: ConvertError
    NO_MEMORY = ...  # type: ConvertError
    PARTIAL_INPUT = ...  # type: ConvertError


class DateDMY(Enum, builtins.int):
    DAY = ...  # type: DateDMY
    MONTH = ...  # type: DateDMY
    YEAR = ...  # type: DateDMY


class DateMonth(Enum, builtins.int):
    APRIL = ...  # type: DateMonth
    AUGUST = ...  # type: DateMonth
    BAD_MONTH = ...  # type: DateMonth
    DECEMBER = ...  # type: DateMonth
    FEBRUARY = ...  # type: DateMonth
    JANUARY = ...  # type: DateMonth
    JULY = ...  # type: DateMonth
    JUNE = ...  # type: DateMonth
    MARCH = ...  # type: DateMonth
    MAY = ...  # type: DateMonth
    NOVEMBER = ...  # type: DateMonth
    OCTOBER = ...  # type: DateMonth
    SEPTEMBER = ...  # type: DateMonth


class DateWeekday(Enum, builtins.int):
    BAD_WEEKDAY = ...  # type: DateWeekday
    FRIDAY = ...  # type: DateWeekday
    MONDAY = ...  # type: DateWeekday
    SATURDAY = ...  # type: DateWeekday
    SUNDAY = ...  # type: DateWeekday
    THURSDAY = ...  # type: DateWeekday
    TUESDAY = ...  # type: DateWeekday
    WEDNESDAY = ...  # type: DateWeekday


class Enum(builtins.int):
    ...


class ErrorType(Enum, builtins.int):
    DIGIT_RADIX = ...  # type: ErrorType
    FLOAT_MALFORMED = ...  # type: ErrorType
    FLOAT_RADIX = ...  # type: ErrorType
    NON_DIGIT_IN_CONST = ...  # type: ErrorType
    UNEXP_EOF = ...  # type: ErrorType
    UNEXP_EOF_IN_COMMENT = ...  # type: ErrorType
    UNEXP_EOF_IN_STRING = ...  # type: ErrorType
    UNKNOWN = ...  # type: ErrorType


class FileError(Enum, builtins.int):
    ACCES = ...  # type: FileError
    AGAIN = ...  # type: FileError
    BADF = ...  # type: FileError
    EXIST = ...  # type: FileError
    FAILED = ...  # type: FileError
    FAULT = ...  # type: FileError
    INTR = ...  # type: FileError
    INVAL = ...  # type: FileError
    IO = ...  # type: FileError
    ISDIR = ...  # type: FileError
    LOOP = ...  # type: FileError
    MFILE = ...  # type: FileError
    NAMETOOLONG = ...  # type: FileError
    NFILE = ...  # type: FileError
    NODEV = ...  # type: FileError
    NOENT = ...  # type: FileError
    NOMEM = ...  # type: FileError
    NOSPC = ...  # type: FileError
    NOSYS = ...  # type: FileError
    NOTDIR = ...  # type: FileError
    NXIO = ...  # type: FileError
    PERM = ...  # type: FileError
    PIPE = ...  # type: FileError
    ROFS = ...  # type: FileError
    TXTBSY = ...  # type: FileError


class IOChannelError(Enum, builtins.int):
    FAILED = ...  # type: IOChannelError
    FBIG = ...  # type: IOChannelError
    INVAL = ...  # type: IOChannelError
    IO = ...  # type: IOChannelError
    ISDIR = ...  # type: IOChannelError
    NOSPC = ...  # type: IOChannelError
    NXIO = ...  # type: IOChannelError
    OVERFLOW = ...  # type: IOChannelError
    PIPE = ...  # type: IOChannelError


class IOError(Enum, builtins.int):
    AGAIN = ...  # type: IOError
    INVAL = ...  # type: IOError
    NONE = ...  # type: IOError
    UNKNOWN = ...  # type: IOError


class IOStatus(Enum, builtins.int):
    AGAIN = ...  # type: IOStatus
    EOF = ...  # type: IOStatus
    ERROR = ...  # type: IOStatus
    NORMAL = ...  # type: IOStatus


class KeyFileError(Enum, builtins.int):
    GROUP_NOT_FOUND = ...  # type: KeyFileError
    INVALID_VALUE = ...  # type: KeyFileError
    KEY_NOT_FOUND = ...  # type: KeyFileError
    NOT_FOUND = ...  # type: KeyFileError
    PARSE = ...  # type: KeyFileError
    UNKNOWN_ENCODING = ...  # type: KeyFileError


class LogWriterOutput(Enum, builtins.int):
    HANDLED = ...  # type: LogWriterOutput
    UNHANDLED = ...  # type: LogWriterOutput


class MarkupError(Enum, builtins.int):
    BAD_UTF8 = ...  # type: MarkupError
    EMPTY = ...  # type: MarkupError
    INVALID_CONTENT = ...  # type: MarkupError
    MISSING_ATTRIBUTE = ...  # type: MarkupError
    PARSE = ...  # type: MarkupError
    UNKNOWN_ATTRIBUTE = ...  # type: MarkupError
    UNKNOWN_ELEMENT = ...  # type: MarkupError


class NormalizeMode(Enum, builtins.int):
    ALL = ...  # type: NormalizeMode
    ALL_COMPOSE = ...  # type: NormalizeMode
    DEFAULT = ...  # type: NormalizeMode
    DEFAULT_COMPOSE = ...  # type: NormalizeMode
    NFC = ...  # type: NormalizeMode
    NFD = ...  # type: NormalizeMode
    NFKC = ...  # type: NormalizeMode
    NFKD = ...  # type: NormalizeMode


class NumberParserError(Enum, builtins.int):
    INVALID = ...  # type: NumberParserError
    OUT_OF_BOUNDS = ...  # type: NumberParserError


class OnceStatus(Enum, builtins.int):
    NOTCALLED = ...  # type: OnceStatus
    PROGRESS = ...  # type: OnceStatus
    READY = ...  # type: OnceStatus


class OptionArg(Enum, builtins.int):
    CALLBACK = ...  # type: OptionArg
    DOUBLE = ...  # type: OptionArg
    FILENAME = ...  # type: OptionArg
    FILENAME_ARRAY = ...  # type: OptionArg
    INT = ...  # type: OptionArg
    INT64 = ...  # type: OptionArg
    NONE = ...  # type: OptionArg
    STRING = ...  # type: OptionArg
    STRING_ARRAY = ...  # type: OptionArg


class OptionError(Enum, builtins.int):
    BAD_VALUE = ...  # type: OptionError
    FAILED = ...  # type: OptionError
    UNKNOWN_OPTION = ...  # type: OptionError


class RegexError(Enum, builtins.int):
    ASSERTION_EXPECTED = ...  # type: RegexError
    BACKTRACKING_CONTROL_VERB_ARGUMENT_FORBIDDEN = ...  # type: RegexError
    BACKTRACKING_CONTROL_VERB_ARGUMENT_REQUIRED = ...  # type: RegexError
    CHARACTER_VALUE_TOO_LARGE = ...  # type: RegexError
    COMPILE = ...  # type: RegexError
    DEFINE_REPETION = ...  # type: RegexError
    DUPLICATE_SUBPATTERN_NAME = ...  # type: RegexError
    EXPRESSION_TOO_LARGE = ...  # type: RegexError
    EXTRA_SUBPATTERN_NAME = ...  # type: RegexError
    HEX_CODE_TOO_LARGE = ...  # type: RegexError
    INCONSISTENT_NEWLINE_OPTIONS = ...  # type: RegexError
    INEXISTENT_SUBPATTERN_REFERENCE = ...  # type: RegexError
    INFINITE_LOOP = ...  # type: RegexError
    INTERNAL = ...  # type: RegexError
    INVALID_CONDITION = ...  # type: RegexError
    INVALID_CONTROL_CHAR = ...  # type: RegexError
    INVALID_DATA_CHARACTER = ...  # type: RegexError
    INVALID_ESCAPE_IN_CHARACTER_CLASS = ...  # type: RegexError
    INVALID_OCTAL_VALUE = ...  # type: RegexError
    INVALID_RELATIVE_REFERENCE = ...  # type: RegexError
    MALFORMED_CONDITION = ...  # type: RegexError
    MALFORMED_PROPERTY = ...  # type: RegexError
    MATCH = ...  # type: RegexError
    MEMORY_ERROR = ...  # type: RegexError
    MISSING_BACK_REFERENCE = ...  # type: RegexError
    MISSING_CONTROL_CHAR = ...  # type: RegexError
    MISSING_DIGIT = ...  # type: RegexError
    MISSING_NAME = ...  # type: RegexError
    MISSING_SUBPATTERN_NAME = ...  # type: RegexError
    MISSING_SUBPATTERN_NAME_TERMINATOR = ...  # type: RegexError
    NAME_TOO_LONG = ...  # type: RegexError
    NOTHING_TO_REPEAT = ...  # type: RegexError
    NOT_SUPPORTED_IN_CLASS = ...  # type: RegexError
    NUMBER_TOO_BIG = ...  # type: RegexError
    OPTIMIZE = ...  # type: RegexError
    POSIX_COLLATING_ELEMENTS_NOT_SUPPORTED = ...  # type: RegexError
    POSIX_NAMED_CLASS_OUTSIDE_CLASS = ...  # type: RegexError
    QUANTIFIERS_OUT_OF_ORDER = ...  # type: RegexError
    QUANTIFIER_TOO_BIG = ...  # type: RegexError
    RANGE_OUT_OF_ORDER = ...  # type: RegexError
    REPLACE = ...  # type: RegexError
    SINGLE_BYTE_MATCH_IN_LOOKBEHIND = ...  # type: RegexError
    STRAY_BACKSLASH = ...  # type: RegexError
    SUBPATTERN_NAME_TOO_LONG = ...  # type: RegexError
    TOO_MANY_BRANCHES_IN_DEFINE = ...  # type: RegexError
    TOO_MANY_CONDITIONAL_BRANCHES = ...  # type: RegexError
    TOO_MANY_FORWARD_REFERENCES = ...  # type: RegexError
    TOO_MANY_SUBPATTERNS = ...  # type: RegexError
    UNKNOWN_BACKTRACKING_CONTROL_VERB = ...  # type: RegexError
    UNKNOWN_POSIX_CLASS_NAME = ...  # type: RegexError
    UNKNOWN_PROPERTY = ...  # type: RegexError
    UNMATCHED_PARENTHESIS = ...  # type: RegexError
    UNRECOGNIZED_CHARACTER = ...  # type: RegexError
    UNRECOGNIZED_ESCAPE = ...  # type: RegexError
    UNTERMINATED_CHARACTER_CLASS = ...  # type: RegexError
    UNTERMINATED_COMMENT = ...  # type: RegexError
    VARIABLE_LENGTH_LOOKBEHIND = ...  # type: RegexError


class SeekType(Enum, builtins.int):
    CUR = ...  # type: SeekType
    END = ...  # type: SeekType
    SET = ...  # type: SeekType


class ShellError(Enum, builtins.int):
    BAD_QUOTING = ...  # type: ShellError
    EMPTY_STRING = ...  # type: ShellError
    FAILED = ...  # type: ShellError


class SliceConfig(Enum, builtins.int):
    ALWAYS_MALLOC = ...  # type: SliceConfig
    BYPASS_MAGAZINES = ...  # type: SliceConfig
    CHUNK_SIZES = ...  # type: SliceConfig
    COLOR_INCREMENT = ...  # type: SliceConfig
    CONTENTION_COUNTER = ...  # type: SliceConfig
    WORKING_SET_MSECS = ...  # type: SliceConfig


class SpawnError(Enum, builtins.int):
    ACCES = ...  # type: SpawnError
    CHDIR = ...  # type: SpawnError
    FAILED = ...  # type: SpawnError
    FORK = ...  # type: SpawnError
    INVAL = ...  # type: SpawnError
    IO = ...  # type: SpawnError
    ISDIR = ...  # type: SpawnError
    LIBBAD = ...  # type: SpawnError
    LOOP = ...  # type: SpawnError
    MFILE = ...  # type: SpawnError
    NAMETOOLONG = ...  # type: SpawnError
    NFILE = ...  # type: SpawnError
    NOENT = ...  # type: SpawnError
    NOEXEC = ...  # type: SpawnError
    NOMEM = ...  # type: SpawnError
    NOTDIR = ...  # type: SpawnError
    PERM = ...  # type: SpawnError
    READ = ...  # type: SpawnError
    TOO_BIG = ...  # type: SpawnError
    TXTBUSY = ...  # type: SpawnError
    _2BIG = ...  # type: SpawnError


class TestFileType(Enum, builtins.int):
    BUILT = ...  # type: TestFileType
    DIST = ...  # type: TestFileType


class TestLogType(Enum, builtins.int):
    ERROR = ...  # type: TestLogType
    LIST_CASE = ...  # type: TestLogType
    MAX_RESULT = ...  # type: TestLogType
    MESSAGE = ...  # type: TestLogType
    MIN_RESULT = ...  # type: TestLogType
    NONE = ...  # type: TestLogType
    SKIP_CASE = ...  # type: TestLogType
    START_BINARY = ...  # type: TestLogType
    START_CASE = ...  # type: TestLogType
    START_SUITE = ...  # type: TestLogType
    STOP_CASE = ...  # type: TestLogType
    STOP_SUITE = ...  # type: TestLogType


class TestResult(Enum, builtins.int):
    FAILURE = ...  # type: TestResult
    INCOMPLETE = ...  # type: TestResult
    SKIPPED = ...  # type: TestResult
    SUCCESS = ...  # type: TestResult


class ThreadError(Enum, builtins.int):
    THREAD_ERROR_AGAIN = ...  # type: ThreadError


class TimeType(Enum, builtins.int):
    DAYLIGHT = ...  # type: TimeType
    STANDARD = ...  # type: TimeType
    UNIVERSAL = ...  # type: TimeType


class TokenType(Enum, builtins.int):
    BINARY = ...  # type: TokenType
    CHAR = ...  # type: TokenType
    COMMA = ...  # type: TokenType
    COMMENT_MULTI = ...  # type: TokenType
    COMMENT_SINGLE = ...  # type: TokenType
    EOF = ...  # type: TokenType
    EQUAL_SIGN = ...  # type: TokenType
    ERROR = ...  # type: TokenType
    FLOAT = ...  # type: TokenType
    HEX = ...  # type: TokenType
    IDENTIFIER = ...  # type: TokenType
    IDENTIFIER_NULL = ...  # type: TokenType
    INT = ...  # type: TokenType
    LEFT_BRACE = ...  # type: TokenType
    LEFT_CURLY = ...  # type: TokenType
    LEFT_PAREN = ...  # type: TokenType
    NONE = ...  # type: TokenType
    OCTAL = ...  # type: TokenType
    RIGHT_BRACE = ...  # type: TokenType
    RIGHT_CURLY = ...  # type: TokenType
    RIGHT_PAREN = ...  # type: TokenType
    STRING = ...  # type: TokenType
    SYMBOL = ...  # type: TokenType


class TraverseType(Enum, builtins.int):
    IN_ORDER = ...  # type: TraverseType
    LEVEL_ORDER = ...  # type: TraverseType
    POST_ORDER = ...  # type: TraverseType
    PRE_ORDER = ...  # type: TraverseType


class UnicodeBreakType(Enum, builtins.int):
    AFTER = ...  # type: UnicodeBreakType
    ALPHABETIC = ...  # type: UnicodeBreakType
    AMBIGUOUS = ...  # type: UnicodeBreakType
    BEFORE = ...  # type: UnicodeBreakType
    BEFORE_AND_AFTER = ...  # type: UnicodeBreakType
    CARRIAGE_RETURN = ...  # type: UnicodeBreakType
    CLOSE_PARANTHESIS = ...  # type: UnicodeBreakType
    CLOSE_PUNCTUATION = ...  # type: UnicodeBreakType
    COMBINING_MARK = ...  # type: UnicodeBreakType
    COMPLEX_CONTEXT = ...  # type: UnicodeBreakType
    CONDITIONAL_JAPANESE_STARTER = ...  # type: UnicodeBreakType
    CONTINGENT = ...  # type: UnicodeBreakType
    EMOJI_BASE = ...  # type: UnicodeBreakType
    EMOJI_MODIFIER = ...  # type: UnicodeBreakType
    EXCLAMATION = ...  # type: UnicodeBreakType
    HANGUL_LVT_SYLLABLE = ...  # type: UnicodeBreakType
    HANGUL_LV_SYLLABLE = ...  # type: UnicodeBreakType
    HANGUL_L_JAMO = ...  # type: UnicodeBreakType
    HANGUL_T_JAMO = ...  # type: UnicodeBreakType
    HANGUL_V_JAMO = ...  # type: UnicodeBreakType
    HEBREW_LETTER = ...  # type: UnicodeBreakType
    HYPHEN = ...  # type: UnicodeBreakType
    IDEOGRAPHIC = ...  # type: UnicodeBreakType
    INFIX_SEPARATOR = ...  # type: UnicodeBreakType
    INSEPARABLE = ...  # type: UnicodeBreakType
    LINE_FEED = ...  # type: UnicodeBreakType
    MANDATORY = ...  # type: UnicodeBreakType
    NEXT_LINE = ...  # type: UnicodeBreakType
    NON_BREAKING_GLUE = ...  # type: UnicodeBreakType
    NON_STARTER = ...  # type: UnicodeBreakType
    NUMERIC = ...  # type: UnicodeBreakType
    OPEN_PUNCTUATION = ...  # type: UnicodeBreakType
    POSTFIX = ...  # type: UnicodeBreakType
    PREFIX = ...  # type: UnicodeBreakType
    QUOTATION = ...  # type: UnicodeBreakType
    REGIONAL_INDICATOR = ...  # type: UnicodeBreakType
    SPACE = ...  # type: UnicodeBreakType
    SURROGATE = ...  # type: UnicodeBreakType
    SYMBOL = ...  # type: UnicodeBreakType
    UNKNOWN = ...  # type: UnicodeBreakType
    WORD_JOINER = ...  # type: UnicodeBreakType
    ZERO_WIDTH_JOINER = ...  # type: UnicodeBreakType
    ZERO_WIDTH_SPACE = ...  # type: UnicodeBreakType


class UnicodeScript(Enum, builtins.int):
    ADLAM = ...  # type: UnicodeScript
    AHOM = ...  # type: UnicodeScript
    ANATOLIAN_HIEROGLYPHS = ...  # type: UnicodeScript
    ARABIC = ...  # type: UnicodeScript
    ARMENIAN = ...  # type: UnicodeScript
    AVESTAN = ...  # type: UnicodeScript
    BALINESE = ...  # type: UnicodeScript
    BAMUM = ...  # type: UnicodeScript
    BASSA_VAH = ...  # type: UnicodeScript
    BATAK = ...  # type: UnicodeScript
    BENGALI = ...  # type: UnicodeScript
    BHAIKSUKI = ...  # type: UnicodeScript
    BOPOMOFO = ...  # type: UnicodeScript
    BRAHMI = ...  # type: UnicodeScript
    BRAILLE = ...  # type: UnicodeScript
    BUGINESE = ...  # type: UnicodeScript
    BUHID = ...  # type: UnicodeScript
    CANADIAN_ABORIGINAL = ...  # type: UnicodeScript
    CARIAN = ...  # type: UnicodeScript
    CAUCASIAN_ALBANIAN = ...  # type: UnicodeScript
    CHAKMA = ...  # type: UnicodeScript
    CHAM = ...  # type: UnicodeScript
    CHEROKEE = ...  # type: UnicodeScript
    COMMON = ...  # type: UnicodeScript
    COPTIC = ...  # type: UnicodeScript
    CUNEIFORM = ...  # type: UnicodeScript
    CYPRIOT = ...  # type: UnicodeScript
    CYRILLIC = ...  # type: UnicodeScript
    DESERET = ...  # type: UnicodeScript
    DEVANAGARI = ...  # type: UnicodeScript
    DOGRA = ...  # type: UnicodeScript
    DUPLOYAN = ...  # type: UnicodeScript
    EGYPTIAN_HIEROGLYPHS = ...  # type: UnicodeScript
    ELBASAN = ...  # type: UnicodeScript
    ELYMAIC = ...  # type: UnicodeScript
    ETHIOPIC = ...  # type: UnicodeScript
    GEORGIAN = ...  # type: UnicodeScript
    GLAGOLITIC = ...  # type: UnicodeScript
    GOTHIC = ...  # type: UnicodeScript
    GRANTHA = ...  # type: UnicodeScript
    GREEK = ...  # type: UnicodeScript
    GUJARATI = ...  # type: UnicodeScript
    GUNJALA_GONDI = ...  # type: UnicodeScript
    GURMUKHI = ...  # type: UnicodeScript
    HAN = ...  # type: UnicodeScript
    HANGUL = ...  # type: UnicodeScript
    HANIFI_ROHINGYA = ...  # type: UnicodeScript
    HANUNOO = ...  # type: UnicodeScript
    HATRAN = ...  # type: UnicodeScript
    HEBREW = ...  # type: UnicodeScript
    HIRAGANA = ...  # type: UnicodeScript
    IMPERIAL_ARAMAIC = ...  # type: UnicodeScript
    INHERITED = ...  # type: UnicodeScript
    INSCRIPTIONAL_PAHLAVI = ...  # type: UnicodeScript
    INSCRIPTIONAL_PARTHIAN = ...  # type: UnicodeScript
    INVALID_CODE = ...  # type: UnicodeScript
    JAVANESE = ...  # type: UnicodeScript
    KAITHI = ...  # type: UnicodeScript
    KANNADA = ...  # type: UnicodeScript
    KATAKANA = ...  # type: UnicodeScript
    KAYAH_LI = ...  # type: UnicodeScript
    KHAROSHTHI = ...  # type: UnicodeScript
    KHMER = ...  # type: UnicodeScript
    KHOJKI = ...  # type: UnicodeScript
    KHUDAWADI = ...  # type: UnicodeScript
    LAO = ...  # type: UnicodeScript
    LATIN = ...  # type: UnicodeScript
    LEPCHA = ...  # type: UnicodeScript
    LIMBU = ...  # type: UnicodeScript
    LINEAR_A = ...  # type: UnicodeScript
    LINEAR_B = ...  # type: UnicodeScript
    LISU = ...  # type: UnicodeScript
    LYCIAN = ...  # type: UnicodeScript
    LYDIAN = ...  # type: UnicodeScript
    MAHAJANI = ...  # type: UnicodeScript
    MAKASAR = ...  # type: UnicodeScript
    MALAYALAM = ...  # type: UnicodeScript
    MANDAIC = ...  # type: UnicodeScript
    MANICHAEAN = ...  # type: UnicodeScript
    MARCHEN = ...  # type: UnicodeScript
    MASARAM_GONDI = ...  # type: UnicodeScript
    MEDEFAIDRIN = ...  # type: UnicodeScript
    MEETEI_MAYEK = ...  # type: UnicodeScript
    MENDE_KIKAKUI = ...  # type: UnicodeScript
    MEROITIC_CURSIVE = ...  # type: UnicodeScript
    MEROITIC_HIEROGLYPHS = ...  # type: UnicodeScript
    MIAO = ...  # type: UnicodeScript
    MODI = ...  # type: UnicodeScript
    MONGOLIAN = ...  # type: UnicodeScript
    MRO = ...  # type: UnicodeScript
    MULTANI = ...  # type: UnicodeScript
    MYANMAR = ...  # type: UnicodeScript
    NABATAEAN = ...  # type: UnicodeScript
    NANDINAGARI = ...  # type: UnicodeScript
    NEWA = ...  # type: UnicodeScript
    NEW_TAI_LUE = ...  # type: UnicodeScript
    NKO = ...  # type: UnicodeScript
    NUSHU = ...  # type: UnicodeScript
    NYIAKENG_PUACHUE_HMONG = ...  # type: UnicodeScript
    OGHAM = ...  # type: UnicodeScript
    OLD_HUNGARIAN = ...  # type: UnicodeScript
    OLD_ITALIC = ...  # type: UnicodeScript
    OLD_NORTH_ARABIAN = ...  # type: UnicodeScript
    OLD_PERMIC = ...  # type: UnicodeScript
    OLD_PERSIAN = ...  # type: UnicodeScript
    OLD_SOGDIAN = ...  # type: UnicodeScript
    OLD_SOUTH_ARABIAN = ...  # type: UnicodeScript
    OLD_TURKIC = ...  # type: UnicodeScript
    OL_CHIKI = ...  # type: UnicodeScript
    ORIYA = ...  # type: UnicodeScript
    OSAGE = ...  # type: UnicodeScript
    OSMANYA = ...  # type: UnicodeScript
    PAHAWH_HMONG = ...  # type: UnicodeScript
    PALMYRENE = ...  # type: UnicodeScript
    PAU_CIN_HAU = ...  # type: UnicodeScript
    PHAGS_PA = ...  # type: UnicodeScript
    PHOENICIAN = ...  # type: UnicodeScript
    PSALTER_PAHLAVI = ...  # type: UnicodeScript
    REJANG = ...  # type: UnicodeScript
    RUNIC = ...  # type: UnicodeScript
    SAMARITAN = ...  # type: UnicodeScript
    SAURASHTRA = ...  # type: UnicodeScript
    SHARADA = ...  # type: UnicodeScript
    SHAVIAN = ...  # type: UnicodeScript
    SIDDHAM = ...  # type: UnicodeScript
    SIGNWRITING = ...  # type: UnicodeScript
    SINHALA = ...  # type: UnicodeScript
    SOGDIAN = ...  # type: UnicodeScript
    SORA_SOMPENG = ...  # type: UnicodeScript
    SOYOMBO = ...  # type: UnicodeScript
    SUNDANESE = ...  # type: UnicodeScript
    SYLOTI_NAGRI = ...  # type: UnicodeScript
    SYRIAC = ...  # type: UnicodeScript
    TAGALOG = ...  # type: UnicodeScript
    TAGBANWA = ...  # type: UnicodeScript
    TAI_LE = ...  # type: UnicodeScript
    TAI_THAM = ...  # type: UnicodeScript
    TAI_VIET = ...  # type: UnicodeScript
    TAKRI = ...  # type: UnicodeScript
    TAMIL = ...  # type: UnicodeScript
    TANGUT = ...  # type: UnicodeScript
    TELUGU = ...  # type: UnicodeScript
    THAANA = ...  # type: UnicodeScript
    THAI = ...  # type: UnicodeScript
    TIBETAN = ...  # type: UnicodeScript
    TIFINAGH = ...  # type: UnicodeScript
    TIRHUTA = ...  # type: UnicodeScript
    UGARITIC = ...  # type: UnicodeScript
    UNKNOWN = ...  # type: UnicodeScript
    VAI = ...  # type: UnicodeScript
    WANCHO = ...  # type: UnicodeScript
    WARANG_CITI = ...  # type: UnicodeScript
    YI = ...  # type: UnicodeScript
    ZANABAZAR_SQUARE = ...  # type: UnicodeScript


class UnicodeType(Enum, builtins.int):
    CLOSE_PUNCTUATION = ...  # type: UnicodeType
    CONNECT_PUNCTUATION = ...  # type: UnicodeType
    CONTROL = ...  # type: UnicodeType
    CURRENCY_SYMBOL = ...  # type: UnicodeType
    DASH_PUNCTUATION = ...  # type: UnicodeType
    DECIMAL_NUMBER = ...  # type: UnicodeType
    ENCLOSING_MARK = ...  # type: UnicodeType
    FINAL_PUNCTUATION = ...  # type: UnicodeType
    FORMAT = ...  # type: UnicodeType
    INITIAL_PUNCTUATION = ...  # type: UnicodeType
    LETTER_NUMBER = ...  # type: UnicodeType
    LINE_SEPARATOR = ...  # type: UnicodeType
    LOWERCASE_LETTER = ...  # type: UnicodeType
    MATH_SYMBOL = ...  # type: UnicodeType
    MODIFIER_LETTER = ...  # type: UnicodeType
    MODIFIER_SYMBOL = ...  # type: UnicodeType
    NON_SPACING_MARK = ...  # type: UnicodeType
    OPEN_PUNCTUATION = ...  # type: UnicodeType
    OTHER_LETTER = ...  # type: UnicodeType
    OTHER_NUMBER = ...  # type: UnicodeType
    OTHER_PUNCTUATION = ...  # type: UnicodeType
    OTHER_SYMBOL = ...  # type: UnicodeType
    PARAGRAPH_SEPARATOR = ...  # type: UnicodeType
    PRIVATE_USE = ...  # type: UnicodeType
    SPACE_SEPARATOR = ...  # type: UnicodeType
    SPACING_MARK = ...  # type: UnicodeType
    SURROGATE = ...  # type: UnicodeType
    TITLECASE_LETTER = ...  # type: UnicodeType
    UNASSIGNED = ...  # type: UnicodeType
    UPPERCASE_LETTER = ...  # type: UnicodeType


class UserDirectory(Enum, builtins.int):
    DIRECTORY_DESKTOP = ...  # type: UserDirectory
    DIRECTORY_DOCUMENTS = ...  # type: UserDirectory
    DIRECTORY_DOWNLOAD = ...  # type: UserDirectory
    DIRECTORY_MUSIC = ...  # type: UserDirectory
    DIRECTORY_PICTURES = ...  # type: UserDirectory
    DIRECTORY_PUBLIC_SHARE = ...  # type: UserDirectory
    DIRECTORY_TEMPLATES = ...  # type: UserDirectory
    DIRECTORY_VIDEOS = ...  # type: UserDirectory
    N_DIRECTORIES = ...  # type: UserDirectory


class VariantClass(Enum, builtins.int):
    ARRAY = ...  # type: VariantClass
    BOOLEAN = ...  # type: VariantClass
    BYTE = ...  # type: VariantClass
    DICT_ENTRY = ...  # type: VariantClass
    DOUBLE = ...  # type: VariantClass
    HANDLE = ...  # type: VariantClass
    INT16 = ...  # type: VariantClass
    INT32 = ...  # type: VariantClass
    INT64 = ...  # type: VariantClass
    MAYBE = ...  # type: VariantClass
    OBJECT_PATH = ...  # type: VariantClass
    SIGNATURE = ...  # type: VariantClass
    STRING = ...  # type: VariantClass
    TUPLE = ...  # type: VariantClass
    UINT16 = ...  # type: VariantClass
    UINT32 = ...  # type: VariantClass
    UINT64 = ...  # type: VariantClass
    VARIANT = ...  # type: VariantClass


class VariantParseError(Enum, builtins.int):
    BASIC_TYPE_EXPECTED = ...  # type: VariantParseError
    CANNOT_INFER_TYPE = ...  # type: VariantParseError
    DEFINITE_TYPE_EXPECTED = ...  # type: VariantParseError
    FAILED = ...  # type: VariantParseError
    INPUT_NOT_AT_END = ...  # type: VariantParseError
    INVALID_CHARACTER = ...  # type: VariantParseError
    INVALID_FORMAT_STRING = ...  # type: VariantParseError
    INVALID_OBJECT_PATH = ...  # type: VariantParseError
    INVALID_SIGNATURE = ...  # type: VariantParseError
    INVALID_TYPE_STRING = ...  # type: VariantParseError
    NO_COMMON_TYPE = ...  # type: VariantParseError
    NUMBER_OUT_OF_RANGE = ...  # type: VariantParseError
    NUMBER_TOO_BIG = ...  # type: VariantParseError
    RECURSION = ...  # type: VariantParseError
    TYPE_ERROR = ...  # type: VariantParseError
    UNEXPECTED_TOKEN = ...  # type: VariantParseError
    UNKNOWN_KEYWORD = ...  # type: VariantParseError
    UNTERMINATED_STRING_CONSTANT = ...  # type: VariantParseError
    VALUE_EXPECTED = ...  # type: VariantParseError


ChildWatchFunc = typing.Callable[[builtins.int, builtins.int, typing.Optional[builtins.object]], None]
ClearHandleFunc = typing.Callable[[builtins.int], None]
CompareDataFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object], typing.Optional[builtins.object]], builtins.int]
CompareFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object]], builtins.int]
CopyFunc = typing.Callable[[builtins.object, typing.Optional[builtins.object]], builtins.object]
DataForeachFunc = typing.Callable[[builtins.int, typing.Optional[builtins.object], typing.Optional[builtins.object]], None]
DestroyNotify = typing.Callable[[typing.Optional[builtins.object]], None]
DuplicateFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object]], typing.Optional[builtins.object]]
EqualFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object]], builtins.bool]
FreeFunc = typing.Callable[[typing.Optional[builtins.object]], None]
Func = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object]], None]
HFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object], typing.Optional[builtins.object]], None]
HRFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object], typing.Optional[builtins.object]], builtins.bool]
HashFunc = typing.Callable[[typing.Optional[builtins.object]], builtins.int]
HookCheckFunc = typing.Callable[[typing.Optional[builtins.object]], builtins.bool]
HookCheckMarshaller = typing.Callable[[Hook, typing.Optional[builtins.object]], builtins.bool]
HookCompareFunc = typing.Callable[[Hook, Hook], builtins.int]
HookFinalizeFunc = typing.Callable[[HookList, Hook], None]
HookFindFunc = typing.Callable[[Hook, typing.Optional[builtins.object]], builtins.bool]
HookFunc = typing.Callable[[typing.Optional[builtins.object]], None]
HookMarshaller = typing.Callable[[Hook, typing.Optional[builtins.object]], None]
IOFunc = typing.Callable[[IOChannel, IOCondition, typing.Optional[builtins.object]], builtins.bool]
LogFunc = typing.Callable[[builtins.str, LogLevelFlags, builtins.str, typing.Optional[builtins.object]], None]
LogWriterFunc = typing.Callable[[LogLevelFlags, typing.Sequence[LogField], typing.Optional[builtins.object]], LogWriterOutput]
NodeForeachFunc = typing.Callable[[Node, typing.Optional[builtins.object]], None]
NodeTraverseFunc = typing.Callable[[Node, typing.Optional[builtins.object]], builtins.bool]
OptionArgFunc = typing.Callable[[builtins.str, builtins.str, typing.Optional[builtins.object]], builtins.bool]
OptionErrorFunc = typing.Callable[[OptionContext, OptionGroup, typing.Optional[builtins.object]], None]
OptionParseFunc = typing.Callable[[OptionContext, OptionGroup, typing.Optional[builtins.object]], builtins.bool]
PollFunc = typing.Callable[[PollFD, builtins.int, builtins.int], builtins.int]
PrintFunc = typing.Callable[[builtins.str], None]
RegexEvalCallback = typing.Callable[[MatchInfo, String, typing.Optional[builtins.object]], builtins.bool]
ScannerMsgFunc = typing.Callable[[Scanner, builtins.str, builtins.bool], None]
SequenceIterCompareFunc = typing.Callable[[SequenceIter, SequenceIter, typing.Optional[builtins.object]], builtins.int]
SourceDisposeFunc = typing.Callable[[Source], None]
SourceDummyMarshal = typing.Callable[[], None]
SourceFunc = typing.Callable[[typing.Optional[builtins.object]], builtins.bool]
SpawnChildSetupFunc = typing.Callable[[typing.Optional[builtins.object]], None]
TestDataFunc = typing.Callable[[typing.Optional[builtins.object]], None]
TestFixtureFunc = typing.Callable[[builtins.object, typing.Optional[builtins.object]], None]
TestFunc = typing.Callable[[], None]
TestLogFatalFunc = typing.Callable[[builtins.str, LogLevelFlags, builtins.str, typing.Optional[builtins.object]], builtins.bool]
ThreadFunc = typing.Callable[[typing.Optional[builtins.object]], typing.Optional[builtins.object]]
TranslateFunc = typing.Callable[[builtins.str, typing.Optional[builtins.object]], builtins.str]
TraverseFunc = typing.Callable[[typing.Optional[builtins.object], typing.Optional[builtins.object], typing.Optional[builtins.object]], builtins.bool]
UnixFDSourceFunc = typing.Callable[[builtins.int, IOCondition, typing.Optional[builtins.object]], builtins.bool]
VoidFunc = typing.Callable[[], None]


def access(filename: builtins.str, mode: builtins.int) -> builtins.int: ...


def ascii_digit_value(c: builtins.int) -> builtins.int: ...


def ascii_dtostr(buffer: builtins.str, buf_len: builtins.int, d: builtins.float) -> builtins.str: ...


def ascii_formatd(buffer: builtins.str, buf_len: builtins.int, format: builtins.str, d: builtins.float) -> builtins.str: ...


def ascii_strcasecmp(s1: builtins.str, s2: builtins.str) -> builtins.int: ...


def ascii_strdown(str: builtins.str, len: builtins.int) -> builtins.str: ...


def ascii_string_to_signed(str: builtins.str, base: builtins.int, min: builtins.int, max: builtins.int) -> typing.Tuple[builtins.bool, builtins.int]: ...


def ascii_string_to_unsigned(str: builtins.str, base: builtins.int, min: builtins.int, max: builtins.int) -> typing.Tuple[builtins.bool, builtins.int]: ...


def ascii_strncasecmp(s1: builtins.str, s2: builtins.str, n: builtins.int) -> builtins.int: ...


def ascii_strtod(nptr: builtins.str) -> typing.Tuple[builtins.float, builtins.str]: ...


def ascii_strtoll(nptr: builtins.str, base: builtins.int) -> typing.Tuple[builtins.int, builtins.str]: ...


def ascii_strtoull(nptr: builtins.str, base: builtins.int) -> typing.Tuple[builtins.int, builtins.str]: ...


def ascii_strup(str: builtins.str, len: builtins.int) -> builtins.str: ...


def ascii_tolower(c: builtins.int) -> builtins.int: ...


def ascii_toupper(c: builtins.int) -> builtins.int: ...


def ascii_xdigit_value(c: builtins.int) -> builtins.int: ...


def assert_warning(log_domain: builtins.str, file: builtins.str, line: builtins.int, pretty_function: builtins.str, expression: builtins.str) -> None: ...


def assertion_message(domain: builtins.str, file: builtins.str, line: builtins.int, func: builtins.str, message: builtins.str) -> None: ...


def assertion_message_cmpstr(domain: builtins.str, file: builtins.str, line: builtins.int, func: builtins.str, expr: builtins.str, arg1: builtins.str, cmp: builtins.str, arg2: builtins.str) -> None: ...


def assertion_message_error(domain: builtins.str, file: builtins.str, line: builtins.int, func: builtins.str, expr: builtins.str, error: Error, error_domain: builtins.int, error_code: builtins.int) -> None: ...


def atexit(func: VoidFunc) -> None: ...


def atomic_int_add(atomic: builtins.int, val: builtins.int) -> builtins.int: ...


def atomic_int_and(atomic: builtins.int, val: builtins.int) -> builtins.int: ...


def atomic_int_compare_and_exchange(atomic: builtins.int, oldval: builtins.int, newval: builtins.int) -> builtins.bool: ...


def atomic_int_dec_and_test(atomic: builtins.int) -> builtins.bool: ...


def atomic_int_exchange_and_add(atomic: builtins.int, val: builtins.int) -> builtins.int: ...


def atomic_int_get(atomic: builtins.int) -> builtins.int: ...


def atomic_int_inc(atomic: builtins.int) -> None: ...


def atomic_int_or(atomic: builtins.int, val: builtins.int) -> builtins.int: ...


def atomic_int_set(atomic: builtins.int, newval: builtins.int) -> None: ...


def atomic_int_xor(atomic: builtins.int, val: builtins.int) -> builtins.int: ...


def atomic_pointer_add(atomic: builtins.object, val: builtins.int) -> builtins.int: ...


def atomic_pointer_and(atomic: builtins.object, val: builtins.int) -> builtins.int: ...


def atomic_pointer_compare_and_exchange(atomic: builtins.object, oldval: typing.Optional[builtins.object], newval: typing.Optional[builtins.object]) -> builtins.bool: ...


def atomic_pointer_get(atomic: builtins.object) -> typing.Optional[builtins.object]: ...


def atomic_pointer_or(atomic: builtins.object, val: builtins.int) -> builtins.int: ...


def atomic_pointer_set(atomic: builtins.object, newval: typing.Optional[builtins.object]) -> None: ...


def atomic_pointer_xor(atomic: builtins.object, val: builtins.int) -> builtins.int: ...


def atomic_rc_box_acquire(mem_block: builtins.object) -> builtins.object: ...


def atomic_rc_box_alloc(block_size: builtins.int) -> builtins.object: ...


def atomic_rc_box_alloc0(block_size: builtins.int) -> builtins.object: ...


def atomic_rc_box_dup(block_size: builtins.int, mem_block: builtins.object) -> builtins.object: ...


def atomic_rc_box_get_size(mem_block: builtins.object) -> builtins.int: ...


def atomic_rc_box_release(mem_block: builtins.object) -> None: ...


def atomic_rc_box_release_full(mem_block: builtins.object, clear_func: DestroyNotify) -> None: ...


def atomic_ref_count_compare(arc: builtins.int, val: builtins.int) -> builtins.bool: ...


def atomic_ref_count_dec(arc: builtins.int) -> builtins.bool: ...


def atomic_ref_count_inc(arc: builtins.int) -> None: ...


def atomic_ref_count_init(arc: builtins.int) -> None: ...


def base64_decode(text: builtins.str) -> builtins.bytes: ...


def base64_decode_inplace(text: builtins.bytes) -> typing.Tuple[builtins.int, builtins.bytes]: ...


def base64_encode(data: typing.Optional[builtins.bytes]) -> builtins.str: ...


def base64_encode_close(break_lines: builtins.bool, state: builtins.int, save: builtins.int) -> typing.Tuple[builtins.int, builtins.bytes, builtins.int, builtins.int]: ...


def base64_encode_step(in_: builtins.bytes, break_lines: builtins.bool, state: builtins.int, save: builtins.int) -> typing.Tuple[builtins.int, builtins.bytes, builtins.int, builtins.int]: ...


def basename(file_name: builtins.str) -> builtins.str: ...


def bit_lock(address: builtins.int, lock_bit: builtins.int) -> None: ...


def bit_nth_lsf(mask: builtins.int, nth_bit: builtins.int) -> builtins.int: ...


def bit_nth_msf(mask: builtins.int, nth_bit: builtins.int) -> builtins.int: ...


def bit_storage(number: builtins.int) -> builtins.int: ...


def bit_trylock(address: builtins.int, lock_bit: builtins.int) -> builtins.bool: ...


def bit_unlock(address: builtins.int, lock_bit: builtins.int) -> None: ...


def bookmark_file_error_quark() -> builtins.int: ...


def build_filenamev(args: typing.Sequence[builtins.str]) -> builtins.str: ...


def build_pathv(separator: builtins.str, args: typing.Sequence[builtins.str]) -> builtins.str: ...


def byte_array_free(array: builtins.bytes, free_segment: builtins.bool) -> builtins.int: ...


def byte_array_free_to_bytes(array: builtins.bytes) -> Bytes: ...


def byte_array_new() -> builtins.bytes: ...


def byte_array_new_take(data: builtins.bytes) -> builtins.bytes: ...


def byte_array_steal(array: builtins.bytes) -> typing.Tuple[builtins.int, builtins.int]: ...


def byte_array_unref(array: builtins.bytes) -> None: ...


def canonicalize_filename(filename: builtins.str, relative_to: typing.Optional[builtins.str]) -> builtins.str: ...


def chdir(path: builtins.str) -> builtins.int: ...


def check_version(required_major: builtins.int, required_minor: builtins.int, required_micro: builtins.int) -> builtins.str: ...


def checksum_type_get_length(checksum_type: ChecksumType) -> builtins.int: ...


def child_watch_add(priority: typing.Any, pid: typing.Any, function: typing.Any, *data: typing.Any) -> None: ...


def child_watch_source_new(pid: builtins.int) -> Source: ...


def clear_error() -> None: ...


def close(fd: builtins.int) -> builtins.bool: ...


def compute_checksum_for_bytes(checksum_type: ChecksumType, data: Bytes) -> builtins.str: ...


def compute_checksum_for_data(checksum_type: ChecksumType, data: builtins.bytes) -> builtins.str: ...


def compute_checksum_for_string(checksum_type: ChecksumType, str: builtins.str, length: builtins.int) -> builtins.str: ...


def compute_hmac_for_bytes(digest_type: ChecksumType, key: Bytes, data: Bytes) -> builtins.str: ...


def compute_hmac_for_data(digest_type: ChecksumType, key: builtins.bytes, data: builtins.bytes) -> builtins.str: ...


def compute_hmac_for_string(digest_type: ChecksumType, key: builtins.bytes, str: builtins.str, length: builtins.int) -> builtins.str: ...


def convert(str: builtins.bytes, to_codeset: builtins.str, from_codeset: builtins.str) -> typing.Tuple[builtins.bytes, builtins.int]: ...


def convert_error_quark() -> builtins.int: ...


def convert_with_fallback(str: builtins.bytes, to_codeset: builtins.str, from_codeset: builtins.str, fallback: builtins.str) -> typing.Tuple[builtins.bytes, builtins.int]: ...


def datalist_foreach(datalist: Data, func: DataForeachFunc, *user_data: typing.Optional[builtins.object]) -> None: ...


def datalist_get_data(datalist: Data, key: builtins.str) -> typing.Optional[builtins.object]: ...


def datalist_get_flags(datalist: Data) -> builtins.int: ...


def datalist_id_get_data(datalist: Data, key_id: builtins.int) -> typing.Optional[builtins.object]: ...


def datalist_set_flags(datalist: Data, flags: builtins.int) -> None: ...


def datalist_unset_flags(datalist: Data, flags: builtins.int) -> None: ...


def dataset_destroy(dataset_location: builtins.object) -> None: ...


def dataset_foreach(dataset_location: builtins.object, func: DataForeachFunc, *user_data: typing.Optional[builtins.object]) -> None: ...


def dataset_id_get_data(dataset_location: builtins.object, key_id: builtins.int) -> typing.Optional[builtins.object]: ...


def date_get_days_in_month(month: DateMonth, year: builtins.int) -> builtins.int: ...


def date_get_monday_weeks_in_year(year: builtins.int) -> builtins.int: ...


def date_get_sunday_weeks_in_year(year: builtins.int) -> builtins.int: ...


def date_is_leap_year(year: builtins.int) -> builtins.bool: ...


def date_strftime(s: builtins.str, slen: builtins.int, format: builtins.str, date: Date) -> builtins.int: ...


def date_time_compare(dt1: builtins.object, dt2: builtins.object) -> builtins.int: ...


def date_time_equal(dt1: builtins.object, dt2: builtins.object) -> builtins.bool: ...


def date_time_hash(datetime: builtins.object) -> builtins.int: ...


def date_valid_day(day: builtins.int) -> builtins.bool: ...


def date_valid_dmy(day: builtins.int, month: DateMonth, year: builtins.int) -> builtins.bool: ...


def date_valid_julian(julian_date: builtins.int) -> builtins.bool: ...


def date_valid_month(month: DateMonth) -> builtins.bool: ...


def date_valid_weekday(weekday: DateWeekday) -> builtins.bool: ...


def date_valid_year(year: builtins.int) -> builtins.bool: ...


def dcgettext(domain: typing.Optional[builtins.str], msgid: builtins.str, category: builtins.int) -> builtins.str: ...


def dgettext(domain: typing.Optional[builtins.str], msgid: builtins.str) -> builtins.str: ...


def dir_make_tmp(tmpl: typing.Optional[builtins.str]) -> builtins.str: ...


def direct_equal(v1: typing.Optional[builtins.object], v2: typing.Optional[builtins.object]) -> builtins.bool: ...


def direct_hash(v: typing.Optional[builtins.object]) -> builtins.int: ...


def dngettext(domain: typing.Optional[builtins.str], msgid: builtins.str, msgid_plural: builtins.str, n: builtins.int) -> builtins.str: ...


def double_equal(v1: builtins.object, v2: builtins.object) -> builtins.bool: ...


def double_hash(v: builtins.object) -> builtins.int: ...


def dpgettext(domain: typing.Optional[builtins.str], msgctxtid: builtins.str, msgidoffset: builtins.int) -> builtins.str: ...


def dpgettext2(domain: typing.Optional[builtins.str], context: builtins.str, msgid: builtins.str) -> builtins.str: ...


def environ_getenv(envp: typing.Optional[typing.Sequence[builtins.str]], variable: builtins.str) -> builtins.str: ...


def environ_setenv(envp: typing.Optional[typing.Sequence[builtins.str]], variable: builtins.str, value: builtins.str, overwrite: builtins.bool) -> typing.Sequence[builtins.str]: ...


def environ_unsetenv(envp: typing.Optional[typing.Sequence[builtins.str]], variable: builtins.str) -> typing.Sequence[builtins.str]: ...


def file_error_from_errno(err_no: builtins.int) -> FileError: ...


def file_error_quark() -> builtins.int: ...


def file_get_contents(filename: builtins.str) -> typing.Tuple[builtins.bool, builtins.bytes]: ...


def file_open_tmp(tmpl: typing.Optional[builtins.str]) -> typing.Tuple[builtins.int, builtins.str]: ...


def file_read_link(filename: builtins.str) -> builtins.str: ...


def file_set_contents(filename: builtins.str, contents: builtins.bytes) -> builtins.bool: ...


def file_test(filename: builtins.str, test: FileTest) -> builtins.bool: ...


def filename_display_basename(filename: builtins.str) -> builtins.str: ...


def filename_display_name(filename: builtins.str) -> builtins.str: ...


def filename_from_uri(uri: builtins.str) -> typing.Tuple[builtins.str, typing.Optional[builtins.str]]: ...


def filename_from_utf8(utf8string: builtins.str, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def filename_to_uri(filename: builtins.str, hostname: typing.Optional[builtins.str]) -> builtins.str: ...


def filename_to_utf8(opsysstring: builtins.str, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def find_program_in_path(program: builtins.str) -> typing.Optional[builtins.str]: ...


def format_size(size: builtins.int) -> builtins.str: ...


def format_size_for_display(size: builtins.int) -> builtins.str: ...


def format_size_full(size: builtins.int, flags: FormatSizeFlags) -> builtins.str: ...


def free(mem: typing.Optional[builtins.object]) -> None: ...


def get_application_name() -> typing.Optional[builtins.str]: ...


def get_charset() -> typing.Tuple[builtins.bool, builtins.str]: ...


def get_codeset() -> builtins.str: ...


def get_console_charset() -> typing.Tuple[builtins.bool, builtins.str]: ...


def get_current_dir() -> builtins.str: ...


def get_current_time(result: TimeVal) -> None: ...


def get_environ() -> typing.Sequence[builtins.str]: ...


def get_filename_charsets() -> typing.Tuple[builtins.bool, typing.Sequence[builtins.str]]: ...


def get_home_dir() -> builtins.str: ...


def get_host_name() -> builtins.str: ...


def get_language_names() -> typing.Sequence[builtins.str]: ...


def get_language_names_with_category(category_name: builtins.str) -> typing.Sequence[builtins.str]: ...


def get_locale_variants(locale: builtins.str) -> typing.Sequence[builtins.str]: ...


def get_monotonic_time() -> builtins.int: ...


def get_num_processors() -> builtins.int: ...


def get_os_info(key_name: builtins.str) -> typing.Optional[builtins.str]: ...


def get_prgname() -> typing.Optional[builtins.str]: ...


def get_real_name() -> builtins.str: ...


def get_real_time() -> builtins.int: ...


def get_system_config_dirs() -> typing.Sequence[builtins.str]: ...


def get_system_data_dirs() -> typing.Sequence[builtins.str]: ...


def get_tmp_dir() -> builtins.str: ...


def get_user_cache_dir() -> builtins.str: ...


def get_user_config_dir() -> builtins.str: ...


def get_user_data_dir() -> builtins.str: ...


def get_user_name() -> builtins.str: ...


def get_user_runtime_dir() -> builtins.str: ...


def get_user_special_dir(directory: UserDirectory) -> builtins.str: ...


def getenv(variable: builtins.str) -> builtins.str: ...


def hash_table_add(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_contains(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_destroy(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...


def hash_table_insert(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_lookup(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> typing.Optional[builtins.object]: ...


def hash_table_lookup_extended(hash_table: typing.Mapping[builtins.object, builtins.object], lookup_key: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...


def hash_table_remove(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_remove_all(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...


def hash_table_replace(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object], value: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_size(hash_table: typing.Mapping[builtins.object, builtins.object]) -> builtins.int: ...


def hash_table_steal(hash_table: typing.Mapping[builtins.object, builtins.object], key: typing.Optional[builtins.object]) -> builtins.bool: ...


def hash_table_steal_all(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...


def hash_table_steal_extended(hash_table: typing.Mapping[builtins.object, builtins.object], lookup_key: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.object, builtins.object]: ...


def hash_table_unref(hash_table: typing.Mapping[builtins.object, builtins.object]) -> None: ...


def hook_destroy(hook_list: HookList, hook_id: builtins.int) -> builtins.bool: ...


def hook_destroy_link(hook_list: HookList, hook: Hook) -> None: ...


def hook_free(hook_list: HookList, hook: Hook) -> None: ...


def hook_insert_before(hook_list: HookList, sibling: typing.Optional[Hook], hook: Hook) -> None: ...


def hook_prepend(hook_list: HookList, hook: Hook) -> None: ...


def hook_unref(hook_list: HookList, hook: Hook) -> None: ...


def hostname_is_ascii_encoded(hostname: builtins.str) -> builtins.bool: ...


def hostname_is_ip_address(hostname: builtins.str) -> builtins.bool: ...


def hostname_is_non_ascii(hostname: builtins.str) -> builtins.bool: ...


def hostname_to_ascii(hostname: builtins.str) -> builtins.str: ...


def hostname_to_unicode(hostname: builtins.str) -> builtins.str: ...


@typing.overload
def idle_add(function: typing.Callable[[], bool], priority: builtins.int = PRIORITY_DEFAULT) -> builtins.int: ...

@typing.overload
def idle_add(priority: builtins.int, function: typing.Callable[[], bool]) -> builtins.int: ...


def idle_remove_by_data(data: typing.Optional[builtins.object]) -> builtins.bool: ...


def idle_source_new() -> Source: ...


def int64_equal(v1: builtins.object, v2: builtins.object) -> builtins.bool: ...


def int64_hash(v: builtins.object) -> builtins.int: ...


def int_equal(v1: builtins.object, v2: builtins.object) -> builtins.bool: ...


def int_hash(v: builtins.object) -> builtins.int: ...


def intern_static_string(string: typing.Optional[builtins.str]) -> builtins.str: ...


def intern_string(string: typing.Optional[builtins.str]) -> builtins.str: ...

class _FileLike(typing.Protocol):
    def fileno(self) -> int: ...

T = typing.TypeVar("T", bound=typing.Union[IOChannel, int, _FileLike])
T1 = typing.TypeVar("T1")
T2 = typing.TypeVar("T2")
T3 = typing.TypeVar("T3")

@typing.overload
def io_add_watch(channel: T, condition: typing.Union[IOCondition, int], func: typing.Callable[[T, IOCondition], bool]) -> int: ...

@typing.overload
def io_add_watch(channel: T, condition: typing.Union[IOCondition, int], func: typing.Callable[[T, IOCondition, T1], bool], user_data1: T1) -> int: ...

@typing.overload
def io_add_watch(channel: T, condition: typing.Union[IOCondition, int], func: typing.Callable[[T, IOCondition, T1, T2], bool], user_data1: T1, user_data2: T2) -> int: ...


def io_channel_error_from_errno(en: builtins.int) -> IOChannelError: ...


def io_channel_error_quark() -> builtins.int: ...


def io_create_watch(channel: IOChannel, condition: IOCondition) -> Source: ...


def key_file_error_quark() -> builtins.int: ...


def listenv() -> typing.Sequence[builtins.str]: ...


def locale_from_utf8(utf8string: builtins.str, len: builtins.int) -> typing.Tuple[builtins.bytes, builtins.int]: ...


def locale_to_utf8(opsysstring: builtins.bytes) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def log_default_handler(log_domain: typing.Optional[builtins.str], log_level: LogLevelFlags, message: typing.Optional[builtins.str], unused_data: typing.Optional[builtins.object]) -> None: ...


def log_remove_handler(log_domain: builtins.str, handler_id: builtins.int) -> None: ...


def log_set_always_fatal(fatal_mask: LogLevelFlags) -> LogLevelFlags: ...


def log_set_fatal_mask(log_domain: builtins.str, fatal_mask: LogLevelFlags) -> LogLevelFlags: ...


def log_set_handler(log_domain: typing.Optional[builtins.str], log_levels: LogLevelFlags, log_func: LogFunc, *user_data: typing.Optional[builtins.object]) -> builtins.int: ...


def log_set_writer_func(*user_data: typing.Optional[builtins.object]) -> None: ...


def log_structured_array(log_level: LogLevelFlags, fields: typing.Sequence[LogField]) -> None: ...


def log_variant(log_domain: typing.Optional[builtins.str], log_level: LogLevelFlags, fields: Variant) -> None: ...


def log_writer_default(log_level: LogLevelFlags, fields: typing.Sequence[LogField], user_data: typing.Optional[builtins.object]) -> LogWriterOutput: ...


def log_writer_format_fields(log_level: LogLevelFlags, fields: typing.Sequence[LogField], use_color: builtins.bool) -> builtins.str: ...


def log_writer_is_journald(output_fd: builtins.int) -> builtins.bool: ...


def log_writer_journald(log_level: LogLevelFlags, fields: typing.Sequence[LogField], user_data: typing.Optional[builtins.object]) -> LogWriterOutput: ...


def log_writer_standard_streams(log_level: LogLevelFlags, fields: typing.Sequence[LogField], user_data: typing.Optional[builtins.object]) -> LogWriterOutput: ...


def log_writer_supports_color(output_fd: builtins.int) -> builtins.bool: ...


def main_context_default() -> MainContext: ...


def main_context_get_thread_default() -> MainContext: ...


def main_context_ref_thread_default() -> MainContext: ...


def main_current_source() -> Source: ...


def main_depth() -> builtins.int: ...


def malloc(n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def malloc0(n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def malloc0_n(n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def malloc_n(n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def markup_error_quark() -> builtins.int: ...


def markup_escape_text(text: builtins.str, length: builtins.int) -> builtins.str: ...


def mem_is_system_malloc() -> builtins.bool: ...


def mem_profile() -> None: ...


def mem_set_vtable(vtable: MemVTable) -> None: ...


def memdup(mem: typing.Optional[builtins.object], byte_size: builtins.int) -> typing.Optional[builtins.object]: ...


def mkdir_with_parents(pathname: builtins.str, mode: builtins.int) -> builtins.int: ...


def nullify_pointer(nullify_location: builtins.object) -> None: ...


def number_parser_error_quark() -> builtins.int: ...


def on_error_query(prg_name: builtins.str) -> None: ...


def on_error_stack_trace(prg_name: builtins.str) -> None: ...


def once_init_enter(location: builtins.object) -> builtins.bool: ...


def once_init_leave(location: builtins.object, result: builtins.int) -> None: ...


def option_error_quark() -> builtins.int: ...


def parse_debug_string(string: typing.Optional[builtins.str], keys: typing.Sequence[DebugKey]) -> builtins.int: ...


def path_get_basename(file_name: builtins.str) -> builtins.str: ...


def path_get_dirname(file_name: builtins.str) -> builtins.str: ...


def path_is_absolute(file_name: builtins.str) -> builtins.bool: ...


def path_skip_root(file_name: builtins.str) -> typing.Optional[builtins.str]: ...


def pattern_match(pspec: PatternSpec, string_length: builtins.int, string: builtins.str, string_reversed: typing.Optional[builtins.str]) -> builtins.bool: ...


def pattern_match_simple(pattern: builtins.str, string: builtins.str) -> builtins.bool: ...


def pattern_match_string(pspec: PatternSpec, string: builtins.str) -> builtins.bool: ...


def pointer_bit_lock(address: builtins.object, lock_bit: builtins.int) -> None: ...


def pointer_bit_trylock(address: builtins.object, lock_bit: builtins.int) -> builtins.bool: ...


def pointer_bit_unlock(address: builtins.object, lock_bit: builtins.int) -> None: ...


def poll(fds: PollFD, nfds: builtins.int, timeout: builtins.int) -> builtins.int: ...


def propagate_error(src: Error) -> typing.Optional[Error]: ...


def quark_from_static_string(string: typing.Optional[builtins.str]) -> builtins.int: ...


def quark_from_string(string: typing.Optional[builtins.str]) -> builtins.int: ...


def quark_to_string(quark: builtins.int) -> builtins.str: ...


def quark_try_string(string: typing.Optional[builtins.str]) -> builtins.int: ...


def random_double() -> builtins.float: ...


def random_double_range(begin: builtins.float, end: builtins.float) -> builtins.float: ...


def random_int() -> builtins.int: ...


def random_int_range(begin: builtins.int, end: builtins.int) -> builtins.int: ...


def random_set_seed(seed: builtins.int) -> None: ...


def rc_box_acquire(mem_block: builtins.object) -> builtins.object: ...


def rc_box_alloc(block_size: builtins.int) -> builtins.object: ...


def rc_box_alloc0(block_size: builtins.int) -> builtins.object: ...


def rc_box_dup(block_size: builtins.int, mem_block: builtins.object) -> builtins.object: ...


def rc_box_get_size(mem_block: builtins.object) -> builtins.int: ...


def rc_box_release(mem_block: builtins.object) -> None: ...


def rc_box_release_full(mem_block: builtins.object, clear_func: DestroyNotify) -> None: ...


def realloc(mem: typing.Optional[builtins.object], n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def realloc_n(mem: typing.Optional[builtins.object], n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def ref_count_compare(rc: builtins.int, val: builtins.int) -> builtins.bool: ...


def ref_count_dec(rc: builtins.int) -> builtins.bool: ...


def ref_count_inc(rc: builtins.int) -> None: ...


def ref_count_init(rc: builtins.int) -> None: ...


def ref_string_acquire(str: builtins.str) -> builtins.str: ...


def ref_string_length(str: builtins.str) -> builtins.int: ...


def ref_string_new(str: builtins.str) -> builtins.str: ...


def ref_string_new_intern(str: builtins.str) -> builtins.str: ...


def ref_string_new_len(str: builtins.str, len: builtins.int) -> builtins.str: ...


def ref_string_release(str: builtins.str) -> None: ...


def regex_check_replacement(replacement: builtins.str) -> typing.Tuple[builtins.bool, builtins.bool]: ...


def regex_error_quark() -> builtins.int: ...


def regex_escape_nul(string: builtins.str, length: builtins.int) -> builtins.str: ...


def regex_escape_string(string: typing.Sequence[builtins.str]) -> builtins.str: ...


def regex_match_simple(pattern: builtins.str, string: builtins.str, compile_options: RegexCompileFlags, match_options: RegexMatchFlags) -> builtins.bool: ...


def regex_split_simple(pattern: builtins.str, string: builtins.str, compile_options: RegexCompileFlags, match_options: RegexMatchFlags) -> typing.Sequence[builtins.str]: ...


def reload_user_special_dirs_cache() -> None: ...


def rmdir(filename: builtins.str) -> builtins.int: ...


def sequence_get(iter: SequenceIter) -> typing.Optional[builtins.object]: ...


def sequence_insert_before(iter: SequenceIter, data: typing.Optional[builtins.object]) -> SequenceIter: ...


def sequence_move(src: SequenceIter, dest: SequenceIter) -> None: ...


def sequence_move_range(dest: SequenceIter, begin: SequenceIter, end: SequenceIter) -> None: ...


def sequence_range_get_midpoint(begin: SequenceIter, end: SequenceIter) -> SequenceIter: ...


def sequence_remove(iter: SequenceIter) -> None: ...


def sequence_remove_range(begin: SequenceIter, end: SequenceIter) -> None: ...


def sequence_set(iter: SequenceIter, data: typing.Optional[builtins.object]) -> None: ...


def sequence_swap(a: SequenceIter, b: SequenceIter) -> None: ...


def set_application_name(application_name: builtins.str) -> None: ...


def set_error_literal(domain: builtins.int, code: builtins.int, message: builtins.str) -> Error: ...


def set_prgname(prgname: builtins.str) -> None: ...


def setenv(variable: builtins.str, value: builtins.str, overwrite: builtins.bool) -> builtins.bool: ...


def shell_error_quark() -> builtins.int: ...


def shell_parse_argv(command_line: builtins.str) -> typing.Tuple[builtins.bool, typing.Sequence[builtins.str]]: ...


def shell_quote(unquoted_string: builtins.str) -> builtins.str: ...


def shell_unquote(quoted_string: builtins.str) -> builtins.str: ...


def slice_alloc(block_size: builtins.int) -> typing.Optional[builtins.object]: ...


def slice_alloc0(block_size: builtins.int) -> typing.Optional[builtins.object]: ...


def slice_copy(block_size: builtins.int, mem_block: typing.Optional[builtins.object]) -> typing.Optional[builtins.object]: ...


def slice_free1(block_size: builtins.int, mem_block: typing.Optional[builtins.object]) -> None: ...


def slice_free_chain_with_offset(block_size: builtins.int, mem_chain: typing.Optional[builtins.object], next_offset: builtins.int) -> None: ...


def slice_get_config(ckey: SliceConfig) -> builtins.int: ...


def slice_get_config_state(ckey: SliceConfig, address: builtins.int, n_values: builtins.int) -> builtins.int: ...


def slice_set_config(ckey: SliceConfig, value: builtins.int) -> None: ...


def source_remove(tag: builtins.int) -> builtins.bool: ...


def source_remove_by_funcs_user_data(funcs: SourceFuncs, user_data: typing.Optional[builtins.object]) -> builtins.bool: ...


def source_remove_by_user_data(user_data: typing.Optional[builtins.object]) -> builtins.bool: ...


def source_set_name_by_id(tag: builtins.int, name: builtins.str) -> None: ...


def spaced_primes_closest(num: builtins.int) -> builtins.int: ...


def spawn_async(working_directory: typing.Optional[builtins.str], argv: typing.Sequence[builtins.str], envp: typing.Optional[typing.Sequence[builtins.str]], flags: SpawnFlags, child_setup: typing.Optional[SpawnChildSetupFunc], *user_data: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.int]: ...


def spawn_async_with_fds(working_directory: typing.Optional[builtins.str], argv: typing.Sequence[builtins.str], envp: typing.Optional[typing.Sequence[builtins.str]], flags: SpawnFlags, child_setup: typing.Optional[SpawnChildSetupFunc], user_data: typing.Optional[builtins.object], stdin_fd: builtins.int, stdout_fd: builtins.int, stderr_fd: builtins.int) -> typing.Tuple[builtins.bool, builtins.int]: ...


def spawn_async_with_pipes(working_directory: typing.Optional[builtins.str], argv: typing.Sequence[builtins.str], envp: typing.Optional[typing.Sequence[builtins.str]], flags: SpawnFlags, child_setup: typing.Optional[SpawnChildSetupFunc], *user_data: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.int, builtins.int, builtins.int, builtins.int]: ...


def spawn_check_exit_status(exit_status: builtins.int) -> builtins.bool: ...


def spawn_close_pid(pid: builtins.int) -> None: ...


def spawn_command_line_async(command_line: builtins.str) -> builtins.bool: ...


def spawn_command_line_sync(command_line: builtins.str) -> typing.Tuple[builtins.bool, builtins.bytes, builtins.bytes, builtins.int]: ...


def spawn_error_quark() -> builtins.int: ...


def spawn_exit_error_quark() -> builtins.int: ...


def spawn_sync(working_directory: typing.Optional[builtins.str], argv: typing.Sequence[builtins.str], envp: typing.Optional[typing.Sequence[builtins.str]], flags: SpawnFlags, child_setup: typing.Optional[SpawnChildSetupFunc], *user_data: typing.Optional[builtins.object]) -> typing.Tuple[builtins.bool, builtins.bytes, builtins.bytes, builtins.int]: ...


def stpcpy(dest: builtins.str, src: builtins.str) -> builtins.str: ...


def str_equal(v1: builtins.object, v2: builtins.object) -> builtins.bool: ...


def str_has_prefix(str: builtins.str, prefix: builtins.str) -> builtins.bool: ...


def str_has_suffix(str: builtins.str, suffix: builtins.str) -> builtins.bool: ...


def str_hash(v: builtins.object) -> builtins.int: ...


def str_is_ascii(str: builtins.str) -> builtins.bool: ...


def str_match_string(search_term: builtins.str, potential_hit: builtins.str, accept_alternates: builtins.bool) -> builtins.bool: ...


def str_to_ascii(str: builtins.str, from_locale: typing.Optional[builtins.str]) -> builtins.str: ...


def str_tokenize_and_fold(string: builtins.str, translit_locale: typing.Optional[builtins.str]) -> typing.Tuple[typing.Sequence[builtins.str], typing.Sequence[builtins.str]]: ...


def strcanon(string: builtins.str, valid_chars: builtins.str, substitutor: builtins.int) -> builtins.str: ...


def strcasecmp(s1: builtins.str, s2: builtins.str) -> builtins.int: ...


def strchomp(string: builtins.str) -> builtins.str: ...


def strchug(string: builtins.str) -> builtins.str: ...


def strcmp0(str1: typing.Optional[builtins.str], str2: typing.Optional[builtins.str]) -> builtins.int: ...


def strcompress(source: builtins.str) -> builtins.str: ...


def strdelimit(string: builtins.str, delimiters: typing.Optional[builtins.str], new_delimiter: builtins.int) -> builtins.str: ...


def strdown(string: builtins.str) -> builtins.str: ...


def strdup(str: typing.Optional[builtins.str]) -> builtins.str: ...


def strerror(errnum: builtins.int) -> builtins.str: ...


def strescape(source: builtins.str, exceptions: typing.Optional[builtins.str]) -> builtins.str: ...


def strfreev(str_array: typing.Optional[builtins.str]) -> None: ...


def string_new(init: typing.Optional[builtins.str]) -> String: ...


def string_new_len(init: builtins.str, len: builtins.int) -> String: ...


def string_sized_new(dfl_size: builtins.int) -> String: ...


def strip_context(msgid: builtins.str, msgval: builtins.str) -> builtins.str: ...


def strjoinv(separator: typing.Optional[builtins.str], str_array: builtins.str) -> builtins.str: ...


def strlcat(dest: builtins.str, src: builtins.str, dest_size: builtins.int) -> builtins.int: ...


def strlcpy(dest: builtins.str, src: builtins.str, dest_size: builtins.int) -> builtins.int: ...


def strncasecmp(s1: builtins.str, s2: builtins.str, n: builtins.int) -> builtins.int: ...


def strndup(str: builtins.str, n: builtins.int) -> builtins.str: ...


def strnfill(length: builtins.int, fill_char: builtins.int) -> builtins.str: ...


def strreverse(string: builtins.str) -> builtins.str: ...


def strrstr(haystack: builtins.str, needle: builtins.str) -> builtins.str: ...


def strrstr_len(haystack: builtins.str, haystack_len: builtins.int, needle: builtins.str) -> builtins.str: ...


def strsignal(signum: builtins.int) -> builtins.str: ...


def strstr_len(haystack: builtins.str, haystack_len: builtins.int, needle: builtins.str) -> builtins.str: ...


def strtod(nptr: builtins.str) -> typing.Tuple[builtins.float, builtins.str]: ...


def strup(string: builtins.str) -> builtins.str: ...


def strv_contains(strv: builtins.str, str: builtins.str) -> builtins.bool: ...


def strv_equal(strv1: builtins.str, strv2: builtins.str) -> builtins.bool: ...


def strv_get_type() -> GObject.GType: ...


def strv_length(str_array: builtins.str) -> builtins.int: ...


def test_add_data_func(testpath: builtins.str, test_data: typing.Optional[builtins.object], test_func: TestDataFunc) -> None: ...


def test_add_data_func_full(testpath: builtins.str, test_data: typing.Optional[builtins.object], test_func: TestDataFunc) -> None: ...


def test_add_func(testpath: builtins.str, test_func: TestFunc) -> None: ...


def test_assert_expected_messages_internal(domain: builtins.str, file: builtins.str, line: builtins.int, func: builtins.str) -> None: ...


def test_bug(bug_uri_snippet: builtins.str) -> None: ...


def test_bug_base(uri_pattern: builtins.str) -> None: ...


def test_expect_message(log_domain: typing.Optional[builtins.str], log_level: LogLevelFlags, pattern: builtins.str) -> None: ...


def test_fail() -> None: ...


def test_failed() -> builtins.bool: ...


def test_get_dir(file_type: TestFileType) -> builtins.str: ...


def test_incomplete(msg: typing.Optional[builtins.str]) -> None: ...


def test_log_type_name(log_type: TestLogType) -> builtins.str: ...


def test_queue_destroy(destroy_func: DestroyNotify, destroy_data: typing.Optional[builtins.object]) -> None: ...


def test_queue_free(gfree_pointer: typing.Optional[builtins.object]) -> None: ...


def test_rand_double() -> builtins.float: ...


def test_rand_double_range(range_start: builtins.float, range_end: builtins.float) -> builtins.float: ...


def test_rand_int() -> builtins.int: ...


def test_rand_int_range(begin: builtins.int, end: builtins.int) -> builtins.int: ...


def test_run() -> builtins.int: ...


def test_run_suite(suite: TestSuite) -> builtins.int: ...


def test_set_nonfatal_assertions() -> None: ...


def test_skip(msg: typing.Optional[builtins.str]) -> None: ...


def test_subprocess() -> builtins.bool: ...


def test_summary(summary: builtins.str) -> None: ...


def test_timer_elapsed() -> builtins.float: ...


def test_timer_last() -> builtins.float: ...


def test_timer_start() -> None: ...


def test_trap_assertions(domain: builtins.str, file: builtins.str, line: builtins.int, func: builtins.str, assertion_flags: builtins.int, pattern: builtins.str) -> None: ...


def test_trap_fork(usec_timeout: builtins.int, test_trap_flags: TestTrapFlags) -> builtins.bool: ...


def test_trap_has_passed() -> builtins.bool: ...


def test_trap_reached_timeout() -> builtins.bool: ...


def test_trap_subprocess(test_path: typing.Optional[builtins.str], usec_timeout: builtins.int, test_flags: TestSubprocessFlags) -> None: ...


def thread_error_quark() -> builtins.int: ...


def thread_exit(retval: typing.Optional[builtins.object]) -> None: ...


def thread_pool_get_max_idle_time() -> builtins.int: ...


def thread_pool_get_max_unused_threads() -> builtins.int: ...


def thread_pool_get_num_unused_threads() -> builtins.int: ...


def thread_pool_set_max_idle_time(interval: builtins.int) -> None: ...


def thread_pool_set_max_unused_threads(max_threads: builtins.int) -> None: ...


def thread_pool_stop_unused_threads() -> None: ...


def thread_self() -> Thread: ...


def thread_yield() -> None: ...


def time_val_from_iso8601(iso_date: builtins.str) -> typing.Tuple[builtins.bool, TimeVal]: ...


def timeout_add(interval: int, function: typing.Callable[..., bool], *data: typing.Optional[object], priority: int = PRIORITY_DEFAULT) -> builtins.int: ...


def timeout_add_seconds(interval: int, function: typing.Callable[..., bool], *data: typing.Optional[object], priority: int = PRIORITY_DEFAULT) -> builtins.int: ...


def timeout_source_new(interval: builtins.int) -> Source: ...


def timeout_source_new_seconds(interval: builtins.int) -> Source: ...


def trash_stack_height(stack_p: TrashStack) -> builtins.int: ...


def trash_stack_peek(stack_p: TrashStack) -> typing.Optional[builtins.object]: ...


def trash_stack_pop(stack_p: TrashStack) -> typing.Optional[builtins.object]: ...


def trash_stack_push(stack_p: TrashStack, data_p: builtins.object) -> None: ...


def try_malloc(n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def try_malloc0(n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def try_malloc0_n(n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def try_malloc_n(n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def try_realloc(mem: typing.Optional[builtins.object], n_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def try_realloc_n(mem: typing.Optional[builtins.object], n_blocks: builtins.int, n_block_bytes: builtins.int) -> typing.Optional[builtins.object]: ...


def ucs4_to_utf16(str: builtins.str, len: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def ucs4_to_utf8(str: builtins.str, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def unichar_break_type(c: builtins.str) -> UnicodeBreakType: ...


def unichar_combining_class(uc: builtins.str) -> builtins.int: ...


def unichar_compose(a: builtins.str, b: builtins.str) -> typing.Tuple[builtins.bool, builtins.str]: ...


def unichar_decompose(ch: builtins.str) -> typing.Tuple[builtins.bool, builtins.str, builtins.str]: ...


def unichar_digit_value(c: builtins.str) -> builtins.int: ...


def unichar_fully_decompose(ch: builtins.str, compat: builtins.bool, result_len: builtins.int) -> typing.Tuple[builtins.int, builtins.str]: ...


def unichar_get_mirror_char(ch: builtins.str, mirrored_ch: builtins.str) -> builtins.bool: ...


def unichar_get_script(ch: builtins.str) -> UnicodeScript: ...


def unichar_isalnum(c: builtins.str) -> builtins.bool: ...


def unichar_isalpha(c: builtins.str) -> builtins.bool: ...


def unichar_iscntrl(c: builtins.str) -> builtins.bool: ...


def unichar_isdefined(c: builtins.str) -> builtins.bool: ...


def unichar_isdigit(c: builtins.str) -> builtins.bool: ...


def unichar_isgraph(c: builtins.str) -> builtins.bool: ...


def unichar_islower(c: builtins.str) -> builtins.bool: ...


def unichar_ismark(c: builtins.str) -> builtins.bool: ...


def unichar_isprint(c: builtins.str) -> builtins.bool: ...


def unichar_ispunct(c: builtins.str) -> builtins.bool: ...


def unichar_isspace(c: builtins.str) -> builtins.bool: ...


def unichar_istitle(c: builtins.str) -> builtins.bool: ...


def unichar_isupper(c: builtins.str) -> builtins.bool: ...


def unichar_iswide(c: builtins.str) -> builtins.bool: ...


def unichar_iswide_cjk(c: builtins.str) -> builtins.bool: ...


def unichar_isxdigit(c: builtins.str) -> builtins.bool: ...


def unichar_iszerowidth(c: builtins.str) -> builtins.bool: ...


def unichar_to_utf8(c: builtins.str) -> typing.Tuple[builtins.int, builtins.str]: ...


def unichar_tolower(c: builtins.str) -> builtins.str: ...


def unichar_totitle(c: builtins.str) -> builtins.str: ...


def unichar_toupper(c: builtins.str) -> builtins.str: ...


def unichar_type(c: builtins.str) -> UnicodeType: ...


def unichar_validate(ch: builtins.str) -> builtins.bool: ...


def unichar_xdigit_value(c: builtins.str) -> builtins.int: ...


def unicode_canonical_decomposition(ch: builtins.str, result_len: builtins.int) -> builtins.str: ...


def unicode_canonical_ordering(string: builtins.str, len: builtins.int) -> None: ...


def unicode_script_from_iso15924(iso15924: builtins.int) -> UnicodeScript: ...


def unicode_script_to_iso15924(script: UnicodeScript) -> builtins.int: ...


def unix_error_quark() -> builtins.int: ...


def unix_fd_add_full(priority: builtins.int, fd: builtins.int, condition: IOCondition, function: UnixFDSourceFunc, *user_data: typing.Optional[builtins.object]) -> builtins.int: ...


def unix_fd_source_new(fd: builtins.int, condition: IOCondition) -> Source: ...


def unix_get_passwd_entry(user_name: builtins.str) -> typing.Optional[builtins.object]: ...


def unix_open_pipe(fds: builtins.int, flags: builtins.int) -> builtins.bool: ...


def unix_set_fd_nonblocking(fd: builtins.int, nonblock: builtins.bool) -> builtins.bool: ...


def unix_signal_add(priority: builtins.int, signum: builtins.int, handler: SourceFunc, *user_data: typing.Optional[builtins.object]) -> builtins.int: ...


def unix_signal_source_new(signum: builtins.int) -> Source: ...


def unlink(filename: builtins.str) -> builtins.int: ...


def unsetenv(variable: builtins.str) -> None: ...


def uri_escape_string(unescaped: builtins.str, reserved_chars_allowed: typing.Optional[builtins.str], allow_utf8: builtins.bool) -> builtins.str: ...


def uri_list_extract_uris(uri_list: builtins.str) -> typing.Sequence[builtins.str]: ...


def uri_parse_scheme(uri: builtins.str) -> builtins.str: ...


def uri_unescape_segment(escaped_string: typing.Optional[builtins.str], escaped_string_end: typing.Optional[builtins.str], illegal_characters: typing.Optional[builtins.str]) -> builtins.str: ...


def uri_unescape_string(escaped_string: builtins.str, illegal_characters: typing.Optional[builtins.str]) -> builtins.str: ...


def usleep(microseconds: builtins.int) -> None: ...


def utf16_to_ucs4(str: builtins.int, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def utf16_to_utf8(str: builtins.int, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def utf8_casefold(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_collate(str1: builtins.str, str2: builtins.str) -> builtins.int: ...


def utf8_collate_key(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_collate_key_for_filename(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_find_next_char(p: builtins.str, end: typing.Optional[builtins.str]) -> typing.Optional[builtins.str]: ...


def utf8_find_prev_char(str: builtins.str, p: builtins.str) -> typing.Optional[builtins.str]: ...


def utf8_get_char(p: builtins.str) -> builtins.str: ...


def utf8_get_char_validated(p: builtins.str, max_len: builtins.int) -> builtins.str: ...


def utf8_make_valid(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_normalize(str: builtins.str, len: builtins.int, mode: NormalizeMode) -> typing.Optional[builtins.str]: ...


def utf8_offset_to_pointer(str: builtins.str, offset: builtins.int) -> builtins.str: ...


def utf8_pointer_to_offset(str: builtins.str, pos: builtins.str) -> builtins.int: ...


def utf8_prev_char(p: builtins.str) -> builtins.str: ...


def utf8_strchr(p: builtins.str, len: builtins.int, c: builtins.str) -> typing.Optional[builtins.str]: ...


def utf8_strdown(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_strlen(p: builtins.str, max: builtins.int) -> builtins.int: ...


def utf8_strncpy(dest: builtins.str, src: builtins.str, n: builtins.int) -> builtins.str: ...


def utf8_strrchr(p: builtins.str, len: builtins.int, c: builtins.str) -> typing.Optional[builtins.str]: ...


def utf8_strreverse(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_strup(str: builtins.str, len: builtins.int) -> builtins.str: ...


def utf8_substring(str: builtins.str, start_pos: builtins.int, end_pos: builtins.int) -> builtins.str: ...


def utf8_to_ucs4(str: builtins.str, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int, builtins.int]: ...


def utf8_to_ucs4_fast(str: builtins.str, len: builtins.int) -> typing.Tuple[builtins.str, builtins.int]: ...


def utf8_to_utf16(str: builtins.str, len: builtins.int) -> typing.Tuple[builtins.int, builtins.int, builtins.int]: ...


def utf8_validate(str: builtins.bytes) -> typing.Tuple[builtins.bool, builtins.str]: ...


def utf8_validate_len(str: builtins.bytes) -> typing.Tuple[builtins.bool, builtins.str]: ...


def uuid_string_is_valid(str: builtins.str) -> builtins.bool: ...


def uuid_string_random() -> builtins.str: ...


def variant_get_gtype() -> GObject.GType: ...


def variant_is_object_path(string: builtins.str) -> builtins.bool: ...


def variant_is_signature(string: builtins.str) -> builtins.bool: ...


def variant_parse(type: typing.Optional[VariantType], text: builtins.str, limit: typing.Optional[builtins.str], endptr: typing.Optional[builtins.str]) -> Variant: ...


def variant_parse_error_print_context(error: Error, source_str: builtins.str) -> builtins.str: ...


def variant_parse_error_quark() -> builtins.int: ...


def variant_parser_get_error_quark() -> builtins.int: ...


def variant_type_checked_(arg0: builtins.str) -> VariantType: ...


def variant_type_string_get_depth_(type_string: builtins.str) -> builtins.int: ...


def variant_type_string_is_valid(type_string: builtins.str) -> builtins.bool: ...


def variant_type_string_scan(string: builtins.str, limit: typing.Optional[builtins.str]) -> typing.Tuple[builtins.bool, builtins.str]: ...


ANALYZER_ANALYZING: builtins.int
ASCII_DTOSTR_BUF_SIZE: builtins.int
BIG_ENDIAN: builtins.int
CSET_A_2_Z: builtins.str
CSET_DIGITS: builtins.str
CSET_a_2_z: builtins.str
DATALIST_FLAGS_MASK: builtins.int
DATE_BAD_DAY: builtins.int
DATE_BAD_JULIAN: builtins.int
DATE_BAD_YEAR: builtins.int
DIR_SEPARATOR: builtins.int
DIR_SEPARATOR_S: builtins.str
E: builtins.float
GINT16_FORMAT: builtins.str
GINT16_MODIFIER: builtins.str
GINT32_FORMAT: builtins.str
GINT32_MODIFIER: builtins.str
GINT64_FORMAT: builtins.str
GINT64_MODIFIER: builtins.str
GINTPTR_FORMAT: builtins.str
GINTPTR_MODIFIER: builtins.str
GNUC_FUNCTION: builtins.str
GNUC_PRETTY_FUNCTION: builtins.str
GSIZE_FORMAT: builtins.str
GSIZE_MODIFIER: builtins.str
GSSIZE_FORMAT: builtins.str
GSSIZE_MODIFIER: builtins.str
GUINT16_FORMAT: builtins.str
GUINT32_FORMAT: builtins.str
GUINT64_FORMAT: builtins.str
GUINTPTR_FORMAT: builtins.str
HAVE_GINT64: builtins.int
HAVE_GNUC_VARARGS: builtins.int
HAVE_GNUC_VISIBILITY: builtins.int
HAVE_GROWING_STACK: builtins.int
HAVE_ISO_VARARGS: builtins.int
HOOK_FLAG_USER_SHIFT: builtins.int
IEEE754_DOUBLE_BIAS: builtins.int
IEEE754_FLOAT_BIAS: builtins.int
IO_ERR: IOCondition
IO_FLAG_APPEND: IOFlags
IO_FLAG_GET_MASK: IOFlags
IO_FLAG_IS_READABLE: IOFlags
IO_FLAG_IS_SEEKABLE: IOFlags
IO_FLAG_IS_WRITEABLE: IOFlags
IO_FLAG_MASK: IOFlags
IO_FLAG_NONBLOCK: IOFlags
IO_FLAG_SET_MASK: IOFlags
IO_HUP: IOCondition
IO_IN: IOCondition
IO_NVAL: IOCondition
IO_OUT: IOCondition
IO_PRI: IOCondition
IO_STATUS_AGAIN: IOStatus
IO_STATUS_EOF: IOStatus
IO_STATUS_ERROR: IOStatus
IO_STATUS_NORMAL: IOStatus
KEY_FILE_DESKTOP_GROUP: builtins.str
KEY_FILE_DESKTOP_KEY_ACTIONS: builtins.str
KEY_FILE_DESKTOP_KEY_CATEGORIES: builtins.str
KEY_FILE_DESKTOP_KEY_COMMENT: builtins.str
KEY_FILE_DESKTOP_KEY_DBUS_ACTIVATABLE: builtins.str
KEY_FILE_DESKTOP_KEY_EXEC: builtins.str
KEY_FILE_DESKTOP_KEY_GENERIC_NAME: builtins.str
KEY_FILE_DESKTOP_KEY_HIDDEN: builtins.str
KEY_FILE_DESKTOP_KEY_ICON: builtins.str
KEY_FILE_DESKTOP_KEY_MIME_TYPE: builtins.str
KEY_FILE_DESKTOP_KEY_NAME: builtins.str
KEY_FILE_DESKTOP_KEY_NOT_SHOW_IN: builtins.str
KEY_FILE_DESKTOP_KEY_NO_DISPLAY: builtins.str
KEY_FILE_DESKTOP_KEY_ONLY_SHOW_IN: builtins.str
KEY_FILE_DESKTOP_KEY_PATH: builtins.str
KEY_FILE_DESKTOP_KEY_STARTUP_NOTIFY: builtins.str
KEY_FILE_DESKTOP_KEY_STARTUP_WM_CLASS: builtins.str
KEY_FILE_DESKTOP_KEY_TERMINAL: builtins.str
KEY_FILE_DESKTOP_KEY_TRY_EXEC: builtins.str
KEY_FILE_DESKTOP_KEY_TYPE: builtins.str
KEY_FILE_DESKTOP_KEY_URL: builtins.str
KEY_FILE_DESKTOP_KEY_VERSION: builtins.str
KEY_FILE_DESKTOP_TYPE_APPLICATION: builtins.str
KEY_FILE_DESKTOP_TYPE_DIRECTORY: builtins.str
KEY_FILE_DESKTOP_TYPE_LINK: builtins.str
LITTLE_ENDIAN: builtins.int
LN10: builtins.float
LN2: builtins.float
LOG_2_BASE_10: builtins.float
LOG_DOMAIN: builtins.int
LOG_FATAL_MASK: builtins.int
LOG_LEVEL_USER_SHIFT: builtins.int
MAJOR_VERSION: builtins.int
MAXDOUBLE: builtins.float
MAXFLOAT: builtins.float
MAXINT: builtins.int
MAXINT16: builtins.int
MAXINT32: builtins.int
MAXINT64: builtins.int
MAXINT8: builtins.int
MAXLONG: builtins.int
MAXOFFSET: builtins.int
MAXSHORT: builtins.int
MAXSIZE: builtins.int
MAXSSIZE: builtins.int
MAXUINT: builtins.int
MAXUINT16: builtins.int
MAXUINT32: builtins.int
MAXUINT64: builtins.int
MAXUINT8: builtins.int
MAXULONG: builtins.int
MAXUSHORT: builtins.int
MICRO_VERSION: builtins.int
MINDOUBLE: builtins.float
MINFLOAT: builtins.float
MININT: builtins.int
MININT16: builtins.int
MININT32: builtins.int
MININT64: builtins.int
MININT8: builtins.int
MINLONG: builtins.int
MINOFFSET: builtins.int
MINOR_VERSION: builtins.int
MINSHORT: builtins.int
MINSSIZE: builtins.int
MODULE_SUFFIX: builtins.str
OPTION_ERROR_BAD_VALUE: OptionError
OPTION_ERROR_FAILED: OptionError
OPTION_ERROR_UNKNOWN_OPTION: OptionError
OPTION_FLAG_FILENAME: OptionFlags
OPTION_FLAG_HIDDEN: OptionFlags
OPTION_FLAG_IN_MAIN: OptionFlags
OPTION_FLAG_NOALIAS: OptionFlags
OPTION_FLAG_NO_ARG: OptionFlags
OPTION_FLAG_OPTIONAL_ARG: OptionFlags
OPTION_FLAG_REVERSE: OptionFlags
OPTION_REMAINING: builtins.str
PDP_ENDIAN: builtins.int
PI: builtins.float
PID_FORMAT: builtins.str
PI_2: builtins.float
PI_4: builtins.float
POLLFD_FORMAT: builtins.str
PRIORITY_DEFAULT: builtins.int
PRIORITY_DEFAULT_IDLE: builtins.int
PRIORITY_HIGH: builtins.int
PRIORITY_HIGH_IDLE: builtins.int
PRIORITY_LOW: builtins.int
SEARCHPATH_SEPARATOR: builtins.int
SEARCHPATH_SEPARATOR_S: builtins.str
SIZEOF_LONG: builtins.int
SIZEOF_SIZE_T: builtins.int
SIZEOF_SSIZE_T: builtins.int
SIZEOF_VOID_P: builtins.int
SOURCE_CONTINUE: builtins.int
SOURCE_REMOVE: builtins.int
SPAWN_CHILD_INHERITS_STDIN: SpawnFlags
SPAWN_DO_NOT_REAP_CHILD: SpawnFlags
SPAWN_FILE_AND_ARGV_ZERO: SpawnFlags
SPAWN_LEAVE_DESCRIPTORS_OPEN: SpawnFlags
SPAWN_SEARCH_PATH: SpawnFlags
SPAWN_STDERR_TO_DEV_NULL: SpawnFlags
SPAWN_STDOUT_TO_DEV_NULL: SpawnFlags
SQRT2: builtins.float
STR_DELIMITERS: builtins.str
SYSDEF_AF_INET: builtins.int
SYSDEF_AF_INET6: builtins.int
SYSDEF_AF_UNIX: builtins.int
SYSDEF_MSG_DONTROUTE: builtins.int
SYSDEF_MSG_OOB: builtins.int
SYSDEF_MSG_PEEK: builtins.int
TEST_OPTION_ISOLATE_DIRS: builtins.str
TIME_SPAN_DAY: builtins.int
TIME_SPAN_HOUR: builtins.int
TIME_SPAN_MILLISECOND: builtins.int
TIME_SPAN_MINUTE: builtins.int
TIME_SPAN_SECOND: builtins.int
UNICHAR_MAX_DECOMPOSITION_LENGTH: builtins.int
URI_RESERVED_CHARS_GENERIC_DELIMITERS: builtins.str
URI_RESERVED_CHARS_SUBCOMPONENT_DELIMITERS: builtins.str
USEC_PER_SEC: builtins.int
USER_DIRECTORY_DESKTOP: UserDirectory
USER_DIRECTORY_DOCUMENTS: UserDirectory
USER_DIRECTORY_DOWNLOAD: UserDirectory
USER_DIRECTORY_MUSIC: UserDirectory
USER_DIRECTORY_PICTURES: UserDirectory
USER_DIRECTORY_PUBLIC_SHARE: UserDirectory
USER_DIRECTORY_TEMPLATES: UserDirectory
USER_DIRECTORY_VIDEOS: UserDirectory
VA_COPY_AS_ARRAY: builtins.int
VERSION_MIN_REQUIRED: builtins.int
WIN32_MSG_HANDLE: builtins.int
glib_version: typing.Tuple[int, int, int]
pyglib_version: typing.Tuple[int, int, int]
