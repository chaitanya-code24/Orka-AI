import tempfile
import unittest
from pathlib import Path

import orka.tools
from orka.core.storage import SQLiteStorage, set_default_storage
from orka.graph.builder import build_graph


class GraphWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage = SQLiteStorage(str(Path(self.temp_dir.name) / "graph-test.db"))
        self.storage.reset()
        set_default_storage(self.storage)

    def test_graph_executes_full_workflow(self):
        app = build_graph()

        result = app.invoke(
            {
                "run_id": "graph-test",
                "input": "create customer Alice in Pune and send email to alice@example.com message Welcome Alice",
                "available_tools": ["create_customer_tool", "send_email_tool"],
                "approval_required_tools": [],
                "approved": False,
                "retry_count": 0,
                "max_retries": 1,
                "context": {},
                "steps": [],
                "current_step": "",
                "tool_result": None,
                "completed_steps": [],
                "final_output": None,
                "errors": [],
                "status": "idle",
            }
        )

        self.assertEqual(result["status"], "end")
        self.assertEqual(result["final_output"]["last_result"]["email"]["to"], "alice@example.com")
        self.assertEqual(len(result["completed_steps"]), 2)

    def test_graph_pauses_before_approval_required_tools(self):
        app = build_graph()

        result = app.invoke(
            {
                "run_id": "graph-test",
                "input": "create customer Alice in Pune",
                "available_tools": ["create_customer_tool"],
                "approval_required_tools": ["create_customer_tool"],
                "approved": False,
                "retry_count": 0,
                "max_retries": 1,
                "context": {},
                "steps": [],
                "current_step": "",
                "tool_result": None,
                "completed_steps": [],
                "final_output": None,
                "errors": [],
                "status": "idle",
            }
        )

        self.assertEqual(result["status"], "awaiting_approval")
        self.assertEqual(result["current_step"], "create_customer_tool")
        self.assertEqual(result["completed_steps"], [])
