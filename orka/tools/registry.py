from orka.services.crm import create_customer_tool
from orka.services.email import send_email_tool

tool_registry = {
    "create_customer_tool": create_customer_tool,
    "send_email_tool": send_email_tool
}
