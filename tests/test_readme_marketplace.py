import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("readme_validator", ROOT / "scripts/validate_readme_plugins.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReadmeMarketplaceTest(unittest.TestCase):
    def test_all_manifests_are_documented_consistently(self):
        self.assertEqual(module.validate(), [])

if __name__ == "__main__":
    unittest.main()
