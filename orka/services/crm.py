from typing import Dict, List
from langchain.tools import tool

customers: List[Dict[str, str]] = []


def create_customer(name: str, city: str) -> Dict[str, str]:
    customer = {
        "id": f"cust_{len(customers) + 1}",
        "name": name,
        "city": city,
        "status": "created",
    }
    customers.append(customer)
    return {
        "success": True,
        "customer": customer,
        "message": f"Customer '{name}' has been created successfully in {city}.",
    }


@tool
def create_customer_tool(name: str, city: str) -> str:
    """Create a new customer in the CRM system.
    
    Args:
        name: Customer name
        city: Customer city
        
    Returns:
        Success message with customer details
    """
    result = create_customer(name, city)
    return str(result)
