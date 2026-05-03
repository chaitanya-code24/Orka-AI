from orka.connectors.base import BaseConnector
from orka.tools.registry import register_tool


class SlackConnector(BaseConnector):
    provider = "slack"
    env_keys = ["SLACK_BOT_TOKEN"]

    def send_message(self, channel: str, text: str) -> dict[str, object]:
        payload = {"channel": channel, "text": text}
        return self.build_result("send_message", payload, f"Slack message queued for {channel}.")


@register_tool("slack_send_message_tool")
def slack_send_message_tool(channel: str, text: str) -> dict[str, object]:
    """Send a Slack message to a channel."""
    return SlackConnector().send_message(channel=channel, text=text)
