import unittest

import orka.tools
from orka.core.exceptions import ToolNotFoundError, ValidationError
from orka.tools.registry import get_tool_definition, invoke_tool


class ToolRegistryTests(unittest.TestCase):
    def test_tool_definition_exposes_parameters(self):
        definition = get_tool_definition("create_customer_tool")

        self.assertEqual(definition.parameters, ["name", "city"])

    def test_invoke_tool_validates_missing_args(self):
        with self.assertRaises(ValidationError):
            invoke_tool("send_email_tool", to="user@example.com")

    def test_unknown_tool_raises_typed_error(self):
        with self.assertRaises(ToolNotFoundError):
            get_tool_definition("missing_tool")


if __name__ == "__main__":
    unittest.main()
