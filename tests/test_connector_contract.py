import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_connector.py"
SECRET_NAMES = (
    "AZURE_DEV_TENANT_ID", "AZURE_DEV_CLIENT_ID",
    "AZURE_DEV_CLIENT_SECRET", "AZURE_DEV_SUBSCRIPTION_ID",
    "MS_STORE_PROD_TENANT_ID", "MS_STORE_PROD_CLIENT_ID",
    "MS_STORE_PROD_CLIENT_SECRET", "MS_STORE_PROD_SELLER_ID",
    "MS_STORE_PROD_PRODUCT_ID",
)


class ConnectorContractTests(unittest.TestCase):
    def run_profile(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        for name in SECRET_NAMES:
            environment.pop(name, None)
        return subprocess.run(
            [sys.executable, str(RUNNER), *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_both_discovery_profiles_stop_without_secrets(self):
        for profile, pod in (("azure-discovery", "azure"), ("store-discovery", "microsoft-store")):
            with self.subTest(profile=profile):
                completed = self.run_profile("--profile", profile)
                self.assertEqual(2, completed.returncode)
                result = json.loads(completed.stdout)
                self.assertEqual("WAITING_CONFIGURATION", result["status"])
                self.assertEqual(pod, result["pod"])
                self.assertNotIn("Bearer ", completed.stdout)
                self.assertNotIn("PRIVATE KEY", completed.stdout)

    def test_mutating_profiles_remain_disabled(self):
        for profile in ("azure-release-prod", "store-release-prod"):
            completed = self.run_profile("--profile", profile, "--approval-ref", "test")
            self.assertEqual(2, completed.returncode)
            self.assertEqual("WAITING_CONFIGURATION", json.loads(completed.stdout)["status"])

    def test_describe_is_non_secret_and_machine_readable(self):
        completed = self.run_profile("--profile", "azure-discovery", "--describe")
        self.assertEqual(0, completed.returncode)
        self.assertEqual("azure-discovery", json.loads(completed.stdout)["id"])


if __name__ == "__main__":
    unittest.main()
