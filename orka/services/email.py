from typing import TypedDict
from datetime import datetime, timezone

from orka.core.storage import get_default_storage
from orka.tools.registry import register_tool


class EmailMessage(TypedDict):
    to: str
    message: str
    status: str


def send_email(to: str, message: str) -> dict[str, object]:
    email: EmailMessage = {
        "to": to,
        "message": message,
        "status": "sent",
    }
    storage = get_default_storage()
    storage.create_email(email, created_at=datetime.now(timezone.utc).isoformat())

    return {
        "success": True,
        "email": email,
        "message": f"Email sent to {to}.",
    }


@register_tool("send_email_tool")
def send_email_tool(to: str, message: str) -> dict[str, object]:
    """Send an email through the demo email service."""
    return send_email(to, message)


def list_emails() -> list[dict[str, object]]:
    return get_default_storage().list_emails()
