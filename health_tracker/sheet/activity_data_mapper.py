import os

from health_tracker.data.activity_data import ActivityData
from health_tracker.utils.mapping_loader import load_activity_mapping, TargetType


class ActivityDataMapper:
    def __init__(self, target_type: TargetType = TargetType.SHEETS):
        self.mapping = load_activity_mapping(target_type)

    def to_updates(self, activity: ActivityData, row: int):
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
                value = activity.date.strftime("%Y-%m-%d %H:%M:%S")
            elif hasattr(activity, field):
                attr = getattr(activity, field)
                value = attr() if callable(attr) else attr
            else:
                value = ""
            
            if value not in ("", None):
                updates.append({"range": f"{col}{row}", "values": [[value]]})
        
        return updates
