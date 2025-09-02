import os
from typing import List
import gspread

from health_tracker.data.day_health_data import DayHealthData
from health_tracker.data.activity_data import ActivityData
from health_tracker.destination.base import Destination
from health_tracker.utils.config_loader import config_get, config_get_path
from health_tracker.destination.mapper.sheets_health_mapper import SheetsHealthMapper
from health_tracker.destination.mapper.sheets_activity_mapper import SheetsActivityMapper


class GoogleSheets(Destination):
    """Destination that writes health & activities data directly into Google Sheets."""

    def __init__(self):
        creds_file = config_get_path('google_sheets.credentials_file')
        if not creds_file or not creds_file.exists():
            raise ValueError("Missing Google Sheets credentials file. Configure in config.yaml")

        gc = gspread.service_account(filename=str(creds_file))

        spreadsheet_url = config_get('google_sheets.spreadsheet_url')
        if not spreadsheet_url:
            raise ValueError("Missing Google Sheets spreadsheet URL. Set GOOGLE_SHEETS_SPREADSHEET_URL env var or configure in config.yaml")

        self.spreadsheet = gc.open_by_url(spreadsheet_url)
        
        self.health_mapper = SheetsHealthMapper()
        self.activity_mapper = SheetsActivityMapper()

    def update_health_data(self, date: str, data: DayHealthData):
        worksheet_name = config_get('google_sheets.worksheets.health', env_key='HEALTH_WORKSHEET_NAME')
        ws = self.spreadsheet.worksheet(worksheet_name)

        row = self._find_or_create_row_by_date(ws, date)
        updates = self.health_mapper.map_health(data)
        
        for update in updates:
            update["range"] = f"{update['range']}{row}"
        
        updates.append({
            "range": f"A{row}",
            "values": [[date]]
        })
        
        self._batch_update(ws, updates)

    def update_activities(self, activities: List[ActivityData]):
        worksheet_name = config_get('google_sheets.worksheets.activities', env_key='ACTIVITIES_WORKSHEET_NAME')
        ws = self.spreadsheet.worksheet(worksheet_name)
        values = ws.get_all_values()
        next_row = len(values) + 1

        batch_requests = []
        for i, activity in enumerate(activities, start=0):
            row = next_row + i
            updates = self.activity_mapper.map(activity)
            
            for update in updates:
                update["range"] = f"{update['range']}{row}"
            
            updates.append({
                "range": f"A{row}",
                "values": [[activity.date.strftime(config_get('data.datetime_format'))]]
            })
            
            batch_requests.extend(updates)

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
