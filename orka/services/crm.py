from typing import TypedDict

from orka.tools.registry import register_tool


class Customer(TypedDict):
    id: str
    name: str
    city: str
    status: str


CUSTOMERS: list[Customer] = []


def create_customer(name: str, city: str) -> dict[str, object]:
    customer: Customer = {
        "id": f"cust_{len(CUSTOMERS) + 1}",
        "name": name,
        "city": city,
        "status": "created",
    }
    CUSTOMERS.append(customer)

    return {
        "success": True,
        "customer": customer,
        "message": f"Customer '{name}' created for {city}.",
    }


@register_tool("create_customer_tool")
def create_customer_tool(name: str, city: str) -> str:
    return str(create_customer(name, city))
