from health_tracker.destination.mapper.abstract_activity_mapper import AbstractActivityMapper
from health_tracker.data.activity_data import ActivityData
from health_tracker.utils.mapping_loader import load_activity_mapping, TargetType


class SheetsActivityMapper(AbstractActivityMapper):
    """Google Sheets activity data mapper"""
    
    def __init__(self):
        self.mapping = load_activity_mapping(TargetType.SHEETS)
    
    def map(self, activity: ActivityData) -> dict:
        """Map activity data to Google Sheets format"""
        updates = []
        
        for col, field in self.mapping.items():
            if field == "date":
                continue
            elif hasattr(activity, field):
                value = getattr(activity, field)
                if value is not None:
                    if field == "url" and value:
                        value = f'=HYPERLINK("{value}";"View")'
                    elif field == "duration_seconds" and isinstance(value, (int, float)):
                        value = f"=TIME(0;0;{value})"
                    
                    updates.append({
                        "range": f"{col}",
                        "values": [[value]]
                    })
        
        return updates 