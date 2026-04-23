from typing import Dict
from langchain.tools import tool


def send_email(to: str, message: str) -> Dict[str, str]:
    return {
        "success": True,
        "to": to,
        "message": message,
        "status": "sent",
        "info": f"Email sent to {to}. Delivery is simulated and will appear in the external mail queue.",
    }


@tool
def send_email_tool(to: str, message: str) -> str:
    """Send an email to a recipient.
    
    Args:
        to: Email recipient
        message: Email message content
        
    Returns:
        Confirmation of email sending
    """
    result = send_email(to, message)
    return str(result)
