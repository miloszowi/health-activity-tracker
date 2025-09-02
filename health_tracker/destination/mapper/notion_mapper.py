from health_tracker.data.activity_data import ActivityData
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.utils.mapping_loader import load_health_mapping, load_activity_mapping, TargetType


class NotionMapper:
    def __init__(self):
        self.health_mapping = load_health_mapping(TargetType.NOTION)
        self.activity_mapping = load_activity_mapping(TargetType.NOTION)

    def map_health(self, dto: DayHealthData) -> dict:
        props = {}

        for dto_field, cfg in self.health_mapping.items():
            value = getattr(dto, dto_field, None)

            if value is None:
                continue

            notion_name = cfg["name"]
            notion_type = cfg["type"]

            if notion_type == "number":
                props[notion_name] = {"number": float(value)}
            elif notion_type == "rich_text":
                props[notion_name] = {
                    "rich_text": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "title":
                props[notion_name] = {
                    "title": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "date":
                props[notion_name] = {"date": {"start": value}}
            elif notion_type == "select":
                props[notion_name] = {"select": {"name": str(value)}}

        return {"properties": props}

    def map_activity(self, dto: ActivityData) -> dict:
        props = {}

        for dto_field, cfg in self.activity_mapping.items():
            value = getattr(dto, dto_field, None)

            if value is None:
                continue

            notion_name = cfg["name"]
            notion_type = cfg["type"]

            if notion_type == "number":
                props[notion_name] = {"number": float(value)}
            elif notion_type == "rich_text":
                props[notion_name] = {
                    "rich_text": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "title":
                props[notion_name] = {
                    "title": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "date":
                props[notion_name] = {"date": {"start": value}}
            elif notion_type == "select":
                props[notion_name] = {"select": {"name": str(value)}}
            elif notion_type == "url":
                props[notion_name] = {"url": str(value)}

        return {"properties": props}
