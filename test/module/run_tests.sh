#!/bin/sh
# Build and run the libblueman C unit/fuzz tests under AddressSanitizer,
# then report gcov line coverage for module/libblueman.c.
#
# Mocks are injected with ld --wrap, so no Bluetooth adapter or root is needed.
set -eu

here=$(dirname "$0")
root=$(cd "$here/../.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

WRAPS="socket close ioctl bind connect malloc \
str2ba hci_for_each_dev hci_open_dev hci_close_dev \
hci_read_rssi hci_read_transmit_power_level \
sdp_connect sdp_close sdp_list_append sdp_service_search_attr_req \
sdp_get_access_protos sdp_uuid_to_proto sdp_list_free sdp_record_free"

wrapflags=""
for w in $WRAPS; do
    wrapflags="$wrapflags -Wl,--wrap=$w"
done

cflags=$(pkg-config --cflags bluez 2>/dev/null || echo "")
libs=$(pkg-config --libs bluez 2>/dev/null || echo "-lbluetooth")

cc=${CC:-gcc}

# shellcheck disable=SC2086
"$cc" -std=c11 -D_GNU_SOURCE -O0 -g -Wall \
    -fsanitize=address -fprofile-arcs -ftest-coverage \
    $cflags \
    "$root/test/module/test_libblueman.c" \
    -o "$work/test_libblueman" \
    $wrapflags $libs

cd "$work"
ASAN_OPTIONS=detect_leaks=1 ./test_libblueman
status=$?

echo
echo "=== coverage: module/libblueman.c ==="
gcov -b -o "$work" "$root/test/module/test_libblueman.c" >/dev/null 2>&1 || true
if [ -f libblueman.c.gcov ]; then
    awk '
        /#####/ { miss++; next }
        /-:/    { next }
        /[0-9]+\*?:/ { hit++ }
        END {
            total = hit + miss
            if (total > 0)
                printf "lines executed: %.2f%% (%d/%d), uncovered: %d\n", \
                    100.0 * hit / total, hit, total, miss
        }
    ' libblueman.c.gcov
    echo "--- uncovered lines ---"
    grep -n "#####" libblueman.c.gcov | sed "s/.*#####:[[:space:]]*//" | head -40 || true
else
    echo "(gcov output not found)"
fi

exit $status
