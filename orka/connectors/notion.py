from orka.connectors.base import BaseConnector
from orka.tools.registry import register_tool


class NotionConnector(BaseConnector):
    provider = "notion"
    env_keys = ["NOTION_API_KEY"]

    def create_page(self, database_id: str, title: str, content: str) -> dict[str, object]:
        payload = {"database_id": database_id, "title": title, "content": content}
        return self.build_result("create_page", payload, f"Notion page queued for '{title}'.")


@register_tool("notion_create_page_tool")
def notion_create_page_tool(database_id: str, title: str, content: str) -> dict[str, object]:
    """Create a Notion page in a configured database."""
    return NotionConnector().create_page(database_id=database_id, title=title, content=content)
