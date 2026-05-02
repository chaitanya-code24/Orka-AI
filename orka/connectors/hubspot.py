from orka.connectors.base import BaseConnector
from orka.tools.registry import register_tool


class HubSpotConnector(BaseConnector):
    provider = "hubspot"
    env_keys = ["HUBSPOT_ACCESS_TOKEN"]

    def create_contact(self, email: str, first_name: str, last_name: str, company: str = "") -> dict[str, object]:
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "company": company,
        }
        return self.build_result("create_contact", payload, f"HubSpot contact queued for {email}.")


@register_tool("hubspot_create_contact_tool")
def hubspot_create_contact_tool(email: str, first_name: str, last_name: str, company: str = "") -> dict[str, object]:
    """Create a HubSpot contact."""
    return HubSpotConnector().create_contact(email=email, first_name=first_name, last_name=last_name, company=company)
