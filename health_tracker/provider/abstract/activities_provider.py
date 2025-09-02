from abc import ABC, abstractmethod
from typing import List
from health_tracker.data.activity_data import ActivityData
from health_tracker.destination.destination import Target


class ActivitiesProvider(ABC):
    def __init__(self, target: Target):
        self.target = target

    @abstractmethod
    def fetch_activities_by_date_range(self, start_date: str, end_date: str) -> List[ActivityData]:
        pass

    @abstractmethod
    def mark_as_processed(self, ids: set) -> None:
        pass