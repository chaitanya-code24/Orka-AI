import json
import tempfile
import unittest
from pathlib import Path

from orka import OrkaAgent
from orka.core.run_store import SQLiteRunStore
from orka.core.storage import SQLiteStorage, set_default_storage
from orka.services import list_customers, list_emails


class OrkaAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "orka-test.db"
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

    def test_run_returns_structured_success_response(self):
        run_store = SQLiteRunStore(self.storage)
        agent = OrkaAgent(str(self.config_path), run_store=run_store)

        result = agent.run("create customer Alice in Pune and send email to alice@example.com message Welcome Alice")

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["output"]["last_result"]["email"]["to"], "alice@example.com")
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(len(run_store.list_runs()), 1)
        self.assertEqual(len(list_customers()), 1)
        self.assertEqual(len(list_emails()), 1)

    def test_run_returns_no_match_response(self):
        agent = OrkaAgent(str(self.config_path), run_store=SQLiteRunStore(self.storage))

        result = agent.run("do something unsupported")

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "end")
        self.assertEqual(result["message"], "No configured workflow steps matched the request.")

    def test_run_can_wait_for_approval_and_resume(self):
        self.config_path.write_text(
            json.dumps(
                {
                    "tools": ["create_customer_tool", "send_email_tool"],
                    "approval_required_tools": ["*"],
                    "storage_path": str(self.storage_path),
                }
            ),
            encoding="utf-8",
        )
        run_store = SQLiteRunStore(self.storage)
        agent = OrkaAgent(str(self.config_path), run_store=run_store)

        pending = agent.run("create customer Alice in Pune and send email to alice@example.com message Welcome Alice")

        self.assertEqual(pending["status"], "awaiting_approval")
        self.assertFalse(pending["success"])
        self.assertEqual(len(pending["steps"]), 0)
        self.assertEqual(len(list_customers()), 0)
        self.assertEqual(pending["output"]["approval"]["planned_steps"], ["create_customer_tool", "send_email_tool"])

        approved = agent.approve_run(pending["run_id"])

        self.assertTrue(approved["success"])
        self.assertEqual(approved["status"], "completed")
        self.assertTrue(approved["approved"])
        self.assertEqual(len(approved["steps"]), 2)
        self.assertEqual(len(list_customers()), 1)
        self.assertEqual(len(list_emails()), 1)


if __name__ == "__main__":
    unittest.main()
