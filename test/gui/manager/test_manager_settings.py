import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from blueman.gui.manager.ManagerSettings import EXPOSED_SETTINGS


class TestManagerSettings(unittest.TestCase):
    def test_every_exposed_option_exists_in_general_schema(self) -> None:
        root = Path(__file__).parents[3]
        document = ET.parse(root / "data" / "org.blueman.gschema.xml")
        schema = document.find(".//schema[@id='org.blueman.general']")
        self.assertIsNotNone(schema)
        assert schema is not None
        schema_keys = {key.attrib["name"] for key in schema.findall("key")}
        self.assertLessEqual(EXPOSED_SETTINGS, schema_keys)


if __name__ == "__main__":
    unittest.main()
