import os
from typing import List
import gspread

from health_tracker.data.day_health_data import DayHealthData
from health_tracker.data.activity_data import ActivityData
from health_tracker.destination.destination import Destination


class GoogleSheets(Destination):
    """Destination that writes health & activities data directly into Google Sheets."""

    def __init__(self):
        creds_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
        if not creds_file:
            raise ValueError("Missing GOOGLE_SHEETS_CREDENTIALS_JSON env var")
        gc = gspread.service_account(filename=creds_file)

        spreadsheet_url = os.getenv("GOOGLE_SHEETS_SPREADSHEET_URL")
        if not spreadsheet_url:
            raise ValueError("Missing GOOGLE_SHEETS_SPREADSHEET_URL env var")

        self.spreadsheet = gc.open_by_url(spreadsheet_url)

    def update_health_data(self, date: str, data: DayHealthData):
        worksheet_name = os.getenv("HEALTH_WORKSHEET_NAME")
        ws = self.spreadsheet.worksheet(worksheet_name)

        row = self._find_or_create_row_by_date(ws, date)
        mapping = os.getenv("HEALTH_COLUMNS", "")
        updates = self._build_updates(mapping, data, row, date=date)

        self._batch_update(ws, updates)

    def update_activities(self, activities: List[ActivityData]):
        worksheet_name = os.getenv("ACTIVITIES_WORKSHEET_NAME")
        ws = self.spreadsheet.worksheet(worksheet_name)
        values = ws.get_all_values()
        next_row = len(values) + 1

        mapping = os.getenv("ACTIVITIES_COLUMNS", "")
        batch_requests = []
        for i, activity in enumerate(activities, start=0):
            row = next_row + i
            batch_requests.extend(self._build_updates(mapping, activity, row))

        self._batch_update(ws, batch_requests)

    def _find_or_create_row_by_date(self, ws, date: str) -> int:
        values = ws.col_values(1)
        if date in values:
            return values.index(date) + 1
        else:
            next_row = len(values) + 1
            ws.update_cell(next_row, 1, date)
            return next_row

    def _batch_update(self, ws, updates: List[dict]):
        if not updates:
            return
        body = {"valueInputOption": "USER_ENTERED", "data": updates}
        ws.spreadsheet.values_batch_update(body)

    def _build_updates(self, mapping: str, obj, row: int, date: str = None):
        updates = []
        for part in mapping.split(","):
            if not part.strip():
                continue
            col, field = part.split(":")
            value = None
            if field == "date" and date:
                value = date
            elif hasattr(obj, field):
                attr = getattr(obj, field)
                value = attr() if callable(attr) else attr
                if hasattr(value, "isoformat"):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")

            if value not in ("", None):
                updates.append({"range": f"{col}{row}", "values": [[value]]})
        return updates
