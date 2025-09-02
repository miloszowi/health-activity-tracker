from health_tracker.destination.mapper.health_mapper import HealthMapper
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.utils.config_loader import config_get
from health_tracker.utils.mapping_loader import load_health_mapping, TargetType


class SheetsHealthMapper(HealthMapper):
    """Google Sheets health data mapper"""
    
    def __init__(self):
        self.mapping = load_health_mapping(TargetType.SHEETS)
        self.ws_title = config_get('google_sheets.worksheets.activities')
    
    def map_health(self, data: DayHealthData) -> dict:
        """Map health data to Google Sheets format"""
        updates = []
        
        for col, field in self.mapping.items():
            if field == "date":
                continue
            elif hasattr(data, field):
                value = getattr(data, field)
                if value is not None:
                    updates.append({
                        "range": f"{col}",
                        "values": [[value]]
                    })
        
        return updates 