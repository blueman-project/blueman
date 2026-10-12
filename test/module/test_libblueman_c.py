"""Run the libblueman C unit/fuzz tests (test_libblueman.c) under the Python
test runner. The heavy lifting is in run_tests.sh, which builds the C harness
with ld --wrap mocks under AddressSanitizer and reports gcov coverage.

Skips gracefully when the C toolchain, AddressSanitizer, or BlueZ headers are
unavailable so the suite still runs on minimal environments.
"""
import os
import shutil
import subprocess
import tempfile
import unittest


_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(_HERE, "run_tests.sh")


def _toolchain_ready() -> bool:
    cc = os.environ.get("CC", "gcc")
    if shutil.which(cc) is None or shutil.which("gcov") is None:
        return False
    probe = (
        "#include <bluetooth/bluetooth.h>\n"
        "#include <bluetooth/sdp.h>\n"
        "int main(void){return 0;}\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "probe.c")
        with open(src, "w") as f:
            f.write(probe)
        try:
            result = subprocess.run(
                [cc, "-fsanitize=address", src, "-o", os.path.join(tmp, "probe"), "-lbluetooth"],
                capture_output=True,
            )
        except OSError:
            return False
        return result.returncode == 0


class TestLibbluemanC(unittest.TestCase):
    @unittest.skipUnless(_toolchain_ready(), "C toolchain / ASan / BlueZ headers unavailable")
    def test_c_unit_and_fuzz_suite_passes(self) -> None:
        result = subprocess.run(["sh", _SCRIPT], capture_output=True, text=True)
        if result.returncode != 0:
            self.fail(f"libblueman C tests failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("0 failures", result.stdout + result.stderr)
        self.assertIn("100.00%", result.stdout + result.stderr)
