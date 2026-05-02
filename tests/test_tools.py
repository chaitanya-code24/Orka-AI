import unittest

import orka.tools
from orka.core.exceptions import ToolNotFoundError, ValidationError
from orka.tools.registry import get_tool_definition, invoke_tool, list_tool_schemas, register_tool


@register_tool
def typed_demo_tool(name: str, count: int = 1, active: bool = True) -> dict[str, object]:
    return {"name": name, "count": count, "active": active}


class ToolRegistryTests(unittest.TestCase):
    def test_tool_definition_exposes_parameters(self):
        definition = get_tool_definition("create_customer_tool")

        self.assertEqual(definition.parameters, ["name", "city"])
        self.assertEqual(definition.parameter_schema[0].type, "string")
        self.assertTrue(definition.parameter_schema[0].required)

    def test_tool_definition_exposes_json_schema(self):
        schema = get_tool_definition("typed_demo_tool").to_schema()

        self.assertEqual(schema["name"], "typed_demo_tool")
        self.assertEqual(schema["parameters"]["properties"]["name"]["type"], "string")
        self.assertEqual(schema["parameters"]["properties"]["count"]["type"], "integer")
        self.assertEqual(schema["parameters"]["properties"]["active"]["type"], "boolean")
        self.assertEqual(schema["parameters"]["required"], ["name"])

    def test_invoke_tool_validates_missing_args(self):
        with self.assertRaises(ValidationError):
            invoke_tool("send_email_tool", to="user@example.com")

    def test_invoke_tool_validates_unknown_args(self):
        with self.assertRaises(ValidationError):
            invoke_tool("typed_demo_tool", name="Alice", unexpected=True)

    def test_invoke_tool_validates_argument_types(self):
        with self.assertRaises(ValidationError):
            invoke_tool("typed_demo_tool", name="Alice", count="two")

    def test_invoke_tool_allows_optional_defaults(self):
        result = invoke_tool("typed_demo_tool", name="Alice")

        self.assertEqual(result["count"], 1)

    def test_list_tool_schemas_exposes_registered_contracts(self):
        schemas = list_tool_schemas()
        names = {schema["name"] for schema in schemas}

        self.assertIn("typed_demo_tool", names)

    def test_unknown_tool_raises_typed_error(self):
        with self.assertRaises(ToolNotFoundError):
            get_tool_definition("missing_tool")


if __name__ == "__main__":
    unittest.main()
