from orka.connectors.base import BaseConnector
from orka.tools.registry import register_tool


class GmailConnector(BaseConnector):
    provider = "gmail"
    env_keys = ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN"]

    def send_email(self, to: str, subject: str, body: str) -> dict[str, object]:
        payload = {"to": to, "subject": subject, "body": body}
        return self.build_result("send_email", payload, f"Gmail email queued for {to}.")


@register_tool("gmail_send_email_tool")
def gmail_send_email_tool(to: str, subject: str, body: str) -> dict[str, object]:
    """Send an email through the Gmail connector."""
    return GmailConnector().send_email(to=to, subject=subject, body=body)
