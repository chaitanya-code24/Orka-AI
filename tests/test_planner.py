import unittest

import orka.tools  # noqa: F401
from orka.graph.planner import LLMPlanner, RuleBasedPlanner


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, prompt: str):
        self.prompt = prompt
        return self.response


class PlannerTests(unittest.TestCase):
    def test_rule_based_planner_matches_existing_demo_flow(self):
        planner = RuleBasedPlanner()

        plan = planner.plan(
            "create customer Alice in Pune and send email to alice@example.com message Welcome Alice",
            ["create_customer_tool", "send_email_tool"],
        )

        self.assertEqual(plan.steps, ["create_customer_tool", "send_email_tool"])
        self.assertEqual(plan.context["customer_name"], "Alice")
        self.assertEqual(plan.context["email_to"], "alice@example.com")

    def test_llm_planner_uses_structured_json_steps(self):
        llm = FakeLLM(
            '{"steps": ["send_email_tool"], "context": {"email_to": "sam@example.com", "email_message": "Hi Sam"}}'
        )
        planner = LLMPlanner(llm)

        plan = planner.plan("email Sam", ["create_customer_tool", "send_email_tool"])

        self.assertEqual(plan.steps, ["send_email_tool"])
        self.assertEqual(plan.context["email_message"], "Hi Sam")
        self.assertIn("Available tools", llm.prompt)

    def test_llm_planner_falls_back_for_invalid_response(self):
        planner = LLMPlanner(FakeLLM("not json"))

        plan = planner.plan("send email to a@example.com message Hello", ["send_email_tool"])

        self.assertEqual(plan.steps, ["send_email_tool"])
        self.assertEqual(plan.context["email_to"], "a@example.com")

    def test_llm_planner_filters_unknown_tools(self):
        planner = LLMPlanner(FakeLLM('{"steps": ["delete_everything"], "context": {}}'))

        plan = planner.plan("delete everything", ["send_email_tool"])

        self.assertEqual(plan.steps, [])


if __name__ == "__main__":
    unittest.main()
