from typing import TypedDict
from uuid import uuid4
from datetime import datetime, timezone

from orka.core.storage import get_default_storage
from orka.tools.registry import register_tool


class Customer(TypedDict):
    id: str
    name: str
    city: str
    status: str


def create_customer(name: str, city: str) -> dict[str, object]:
    customer: Customer = {
        "id": f"cust_{uuid4().hex[:12]}",
        "name": name,
        "city": city,
        "status": "created",
    }
    storage = get_default_storage()
    storage.create_customer(customer, created_at=datetime.now(timezone.utc).isoformat())

    return {
        "success": True,
        "customer": customer,
        "message": f"Customer '{name}' created for {city}.",
    }


@register_tool("create_customer_tool")
def create_customer_tool(name: str, city: str) -> dict[str, object]:
    """Create a customer record in the CRM service."""
    return create_customer(name, city)


def list_customers() -> list[dict[str, object]]:
    return get_default_storage().list_customers()
