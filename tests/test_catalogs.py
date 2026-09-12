import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_capability_ids_are_unique_and_normalized(self):
        all_ids = []
        for name in ("azure-capabilities.json", "microsoft-store-capabilities.json"):
            document = json.loads((ROOT / "catalog" / name).read_text(encoding="utf-8"))
            capabilities = document["capabilities"]
            self.assertGreaterEqual(len(capabilities), 15)
            for capability in capabilities:
                self.assertTrue({"id", "feature", "method", "path", "command", "input", "output", "permission", "risk", "monitor", "cost"} <= capability.keys())
                self.assertIn(capability["risk"], {"read_only", "controlled", "approval_required", "manual_only"})
                all_ids.append(capability["id"])
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_accounts_contain_references_not_values(self):
        accounts = json.loads((ROOT / "config" / "accounts.json").read_text(encoding="utf-8"))["accounts"]
        for account in accounts.values():
            for reference in account["credentials"].values():
                self.assertTrue(reference.startswith("env://"))

    def test_manifest_has_separate_pods(self):
        manifest = json.loads((ROOT / "connector.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({"azure", "microsoft-store"}, set(manifest["pods"]))
        self.assertEqual("independent", manifest["pods"]["azure"]["credential_boundary"])
        self.assertEqual("independent", manifest["pods"]["microsoft-store"]["credential_boundary"])


if __name__ == "__main__":
    unittest.main()

