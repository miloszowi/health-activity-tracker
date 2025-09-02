import os

from health_tracker.data.day_health_data import DayHealthData
from health_tracker.utils.mapping_loader import load_health_mapping, TargetType


class HealthDataMapper:
    def __init__(self, target_type: TargetType = TargetType.SHEETS):
        self.mapping = load_health_mapping(target_type)

    def to_updates(self, data: DayHealthData, row: int, date: str):
        updates = []
        
        for col, field_config in self.mapping.items():
            if isinstance(field_config, str):
                if ":" in field_config:
                    col, field = field_config.split(":", 1)
                else:
                    field = field_config
            else:
                field = field_config
            
            if field == "date":
                value = date
            elif hasattr(data, field):
                value = getattr(data, field, "")
            else:
                value = ""
            
            if value not in ("", None):
                updates.append({"range": f"{col}{row}", "values": [[value]]})
        
        return updates