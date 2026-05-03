import os
import unittest
from unittest.mock import patch

import orka.tools  # noqa: F401
from orka.connectors.gmail import GmailConnector
from orka.core.exceptions import ConfigError
from orka.tools import get_tool_definition, invoke_tool, list_tool_schemas


class ConnectorTests(unittest.TestCase):
    def test_connector_tools_are_registered(self):
        tool_names = {schema["name"] for schema in list_tool_schemas()}

        self.assertIn("gmail_send_email_tool", tool_names)
        self.assertIn("google_sheets_append_row_tool", tool_names)
        self.assertIn("notion_create_page_tool", tool_names)
        self.assertIn("hubspot_create_contact_tool", tool_names)
        self.assertIn("slack_send_message_tool", tool_names)

    def test_connector_tool_schema_exposes_required_fields(self):
        schema = get_tool_definition("slack_send_message_tool").to_schema()

        self.assertEqual(schema["parameters"]["required"], ["channel", "text"])
        self.assertEqual(schema["parameters"]["properties"]["channel"]["type"], "string")

    def test_gmail_connector_runs_in_demo_mode_without_credentials(self):
        with patch.dict(os.environ, {"ORKA_CONNECTOR_MODE": "demo"}, clear=False):
            result = invoke_tool(
                "gmail_send_email_tool",
                to="alice@example.com",
                subject="Welcome",
                body="Hello Alice",
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["provider"], "gmail")
        self.assertEqual(result["mode"], "demo")
        self.assertEqual(result["payload"]["to"], "alice@example.com")

    def test_connector_live_mode_requires_credentials(self):
        with patch.dict(os.environ, {"ORKA_CONNECTOR_MODE": "live"}, clear=True):
            with self.assertRaises(ConfigError):
                GmailConnector()

    def test_google_sheets_values_are_split_into_row_fields(self):
        result = invoke_tool(
            "google_sheets_append_row_tool",
            spreadsheet_id="sheet_123",
            sheet_name="Leads",
            values="Alice, Pune, alice@example.com",
        )

        self.assertEqual(result["payload"]["values"], ["Alice", "Pune", "alice@example.com"])


if __name__ == "__main__":
    unittest.main()
