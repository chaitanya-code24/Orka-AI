from orka.connectors.base import BaseConnector
from orka.tools.registry import register_tool


class GoogleSheetsConnector(BaseConnector):
    provider = "google_sheets"
    env_keys = ["GOOGLE_SERVICE_ACCOUNT_JSON"]

    def append_row(self, spreadsheet_id: str, sheet_name: str, values: str) -> dict[str, object]:
        payload = {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "values": [value.strip() for value in values.split(",") if value.strip()],
        }
        return self.build_result("append_row", payload, f"Google Sheets row queued for {sheet_name}.")


@register_tool("google_sheets_append_row_tool")
def google_sheets_append_row_tool(spreadsheet_id: str, sheet_name: str, values: str) -> dict[str, object]:
    """Append a comma-separated row to a Google Sheet."""
    return GoogleSheetsConnector().append_row(spreadsheet_id=spreadsheet_id, sheet_name=sheet_name, values=values)
