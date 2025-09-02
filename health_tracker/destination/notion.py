import os
from typing import List
from health_tracker.data.activity_data import ActivityData
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.destination.base import Destination
from health_tracker.utils.config_loader import config_get
from notion_client import Client
from health_tracker.destination.mapper.notion_mapper import NotionMapper


class Notion(Destination):
    def __init__(self):
        self.client = Client(auth=os.environ.get("NOTION_SECRET"))
        self.mapper = NotionMapper()

    def update_health_data(self, date: str, data: DayHealthData) -> None:
        data = self.mapper.map_health(data)
        database_id = config_get('notion.databases.health', env_key='NOTION_HEALTH_DATABASE_ID')
        if not database_id:
            raise ValueError("Missing Notion health database ID. Set NOTION_HEALTH_DATABASE_ID env var or configure in config.yaml")
        
        page_id = self._get_or_create_page(database_id, date)

        self.client.pages.update(
            page_id=page_id,
            properties=data.get("properties")
        )

    def update_activities(self, activities: List[ActivityData]) -> None:
        database_id = config_get('notion.databases.activities', env_key='NOTION_ACTIVITIES_DATABASE_ID')
        if not database_id:
            raise ValueError("Missing Notion activities database ID. Set NOTION_ACTIVITIES_DATABASE_ID env var or configure in config.yaml")

        for activity in activities:
            page_id = self._get_or_create_page(database_id, activity.date.strftime("%Y-%m-%d %H:%M:%S"))
            data = self.mapper.map_activity(activity)

            self.client.pages.update(
                page_id=page_id,
                properties=data.get("properties")
            )


    def _get_or_create_page(self, database_id: str, date: str) -> str:
        """Returns page_id"""
        query = self.client.databases.query(
            **{
                "database_id": database_id,
                "filter": {
                    "property": "Title",
                    "title": {
                        "equals": date
                    }
                }
            }
        )

        results = query.get("results", [])
        if results:
            page = results[0]
            return page["id"]
        else:
            return self._create_page(database_id, date)

    def _create_page(self, database_id: str, date: str):
        """Returns page_id"""
        import logging

        iso_date = self._normalize_date(date)

        page = self.client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [
                        {"text": {"content": date}}
                    ]
                },
                "Date": {
                    "date": {"start": iso_date}
                }
            }
        )
        return page["id"]

    def _normalize_date(self, date_str: str) -> str:
        """Ensure date string is ISO8601 for Notion Date property."""
        if "T" not in date_str and " " in date_str:
            date_str = date_str.replace(" ", "T", 1)
        return date_str
