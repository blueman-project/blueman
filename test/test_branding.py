import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
BRANDING_PATH = ROOT / "data" / "branding.json"
READER_PATH = ROOT / "build-aux" / "branding.py"


def load_reader():
    spec = importlib.util.spec_from_file_location("branding_reader", READER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBranding(unittest.TestCase):
    def test_branding_input_has_every_generated_value(self) -> None:
        reader = load_reader()
        values = reader.load(BRANDING_PATH)

        self.assertEqual(set(values), set(reader.KEYS))
        self.assertTrue(all(values.values()))

    def test_templates_only_use_declared_brand_placeholders(self) -> None:
        values = json.loads(BRANDING_PATH.read_text(encoding="utf-8"))
        declared = {f"@{name}@" for name in load_reader().KEYS.values()}
        templates = (
            ROOT / "blueman" / "Constants.py.in",
            ROOT / "data" / "blueman.desktop.in.in",
            ROOT / "data" / "blueman-manager.desktop.in.in",
            ROOT / "data" / "org.blueman.Blueman.metainfo.xml.in.in",
        )

        used = {
            token
            for path in templates
            for token in declared
            if token in path.read_text(encoding="utf-8")
        }
        self.assertEqual(used, declared)
        self.assertEqual(set(values), set(load_reader().KEYS))


if __name__ == "__main__":
    unittest.main()
