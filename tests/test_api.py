import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from orka.core.storage import SQLiteStorage, set_default_storage


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "api-test.db"
        self.config_path = Path(self.temp_dir.name) / "config.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "tools": ["create_customer_tool", "send_email_tool"],
                    "storage_path": str(self.storage_path),
                }
            ),
            encoding="utf-8",
        )
        self.storage = SQLiteStorage(str(self.storage_path))
        self.storage.reset()
        set_default_storage(self.storage)

    def test_run_endpoints_work(self):
        import os
        from orka.main import create_app, get_agent

        os.environ["ORKA_CONFIG_PATH"] = str(self.config_path)
        get_agent.cache_clear()
        client = TestClient(create_app())

        create_response = client.post(
            "/runs",
            json={"query": "create customer Alice in Pune and send email to alice@example.com message Welcome Alice"},
        )
        self.assertEqual(create_response.status_code, 200)
        payload = create_response.json()
        self.assertTrue(payload["success"])

        list_response = client.get("/runs")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        get_response = client.get(f"/runs/{payload['run_id']}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["run_id"], payload["run_id"])


if __name__ == "__main__":
    unittest.main()
