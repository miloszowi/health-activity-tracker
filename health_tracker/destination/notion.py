import os
from typing import List
from health_tracker.data.activity_data import ActivityData
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.destination.destination import Destination
from notion_client import Client
from health_tracker.destination.mapper.notion_mapper import NotionMapper


class Notion(Destination):
    def update_health_data(self, date: str, data: DayHealthData) -> None:
        client = Client(auth=os.environ.get("NOTION_SECRET"))
        query = client.databases.query(
            **{
                "database_id": os.environ.get("NOTION_DATABASE_ID"),
                "filter": {
                    "property": "Date",
                    "title": {
                        "equals": date
                    }
                }
            }
        )
        results = query.get("results", [])
        if results:
            page = results[0]
            page_id = page["id"]
        else:
            page = client.pages.create(
                parent={"database_id": os.environ.get("NOTION_DATABASE_ID")},
                properties={
                    "Date": {
                        "title": [
                            {"text": {"content": date}}
                        ]
                    }
                }
            )
            page_id = page["id"]

        notion_mapper = NotionMapper()
        data = notion_mapper.map(data)
        print(data)

        client.pages.update(
            page_id=page_id,
            properties=data.get("properties")
        )

    def update_activities(self, activities: List[ActivityData]) -> None:
        pass
