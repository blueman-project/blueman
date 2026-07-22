#!/usr/bin/env bash
# Compare the ManagerDeviceList row-path benchmark between the current branch
# and main, then assert the branch is at least MIN_GAIN% faster.
#
# Usage: test/benchmarks/run_compare.sh [iterations] [base_ref]
#
# Models each device["Key"] / get_properties() as one synchronous D-Bus
# round-trip (see bench_manager_device_list.py). The headline metric is the
# modeled wall time (CPU + round-trips * DBUS_RTT); round-trip count is the
# deterministic underlying driver.
set -euo pipefail

ITERS="${1:-10000}"
BASE_REF="${2:-main}"
MIN_GAIN=5

# blueman.Constants is generated at build time; the benchmark stubs it, but the
# package must be importable from the tree under test, hence PYTHONPATH.
PY="${PYTHON:-/usr/bin/python3}"

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
BENCH="test/benchmarks/bench_manager_device_list.py"
WORKTREE="$(mktemp -d)/base"

cleanup() { git -C "$REPO_ROOT" worktree remove --force "$WORKTREE" 2>/dev/null || true; }
trap cleanup EXIT

echo "Benchmark: $BENCH  (iterations=$ITERS, dbus model in-script)"

BRANCH_REV="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
echo "=== current branch ($BRANCH_REV) ==="
BRANCH_JSON="$(cd "$REPO_ROOT" && PYTHONPATH="$REPO_ROOT" "$PY" "$BENCH" "$ITERS")"
echo "$BRANCH_JSON"

git -C "$REPO_ROOT" worktree add -q "$WORKTREE" "$BASE_REF"
cp "$REPO_ROOT/$BENCH" "$WORKTREE/bench_base.py"
BASE_REV="$(git -C "$WORKTREE" rev-parse --short HEAD)"
echo "=== base $BASE_REF ($BASE_REV) ==="
BASE_JSON="$(cd "$WORKTREE" && PYTHONPATH="$WORKTREE" "$PY" bench_base.py "$ITERS")"
echo "$BASE_JSON"

echo "=== result ==="
BRANCH_JSON="$BRANCH_JSON" BASE_JSON="$BASE_JSON" MIN_GAIN="$MIN_GAIN" "$PY" - <<'PYEOF'
import json, os, sys
br = json.loads(os.environ["BRANCH_JSON"])
base = json.loads(os.environ["BASE_JSON"])
min_gain = float(os.environ["MIN_GAIN"])

def pct(old, new):
    return (old - new) / old * 100

rt_gain = pct(base["roundtrips_per_iter"], br["roundtrips_per_iter"])
t_gain = pct(base["modeled_seconds"], br["modeled_seconds"])
print(f"D-Bus round-trips/iter: base={base['roundtrips_per_iter']:.0f} "
      f"branch={br['roundtrips_per_iter']:.0f} -> {rt_gain:.1f}% fewer")
print(f"Modeled wall time:      base={base['modeled_seconds']:.2f}s "
      f"branch={br['modeled_seconds']:.2f}s -> {t_gain:.1f}% faster "
      f"({base['modeled_seconds']/br['modeled_seconds']:.1f}x)")
if t_gain >= min_gain:
    print(f"PASS: {t_gain:.1f}% >= {min_gain}% target")
    sys.exit(0)
print(f"FAIL: {t_gain:.1f}% < {min_gain}% target")
sys.exit(1)
PYEOF
