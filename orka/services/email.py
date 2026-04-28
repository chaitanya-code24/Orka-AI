from typing import TypedDict

from orka.tools.registry import register_tool


class EmailMessage(TypedDict):
    to: str
    message: str
    status: str


SENT_EMAILS: list[EmailMessage] = []


def send_email(to: str, message: str) -> dict[str, object]:
    email: EmailMessage = {
        "to": to,
        "message": message,
        "status": "sent",
    }
    SENT_EMAILS.append(email)

    return {
        "success": True,
        "email": email,
        "message": f"Email sent to {to}.",
    }


@register_tool("send_email_tool")
def send_email_tool(to: str, message: str) -> str:
    return str(send_email(to, message))
