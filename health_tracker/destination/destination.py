from abc import ABC, abstractmethod
from typing import List
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.data.activity_data import ActivityData

class Destination(ABC):
    @abstractmethod
    def update_health_data(self, date: str, data: DayHealthData) -> None:
        pass

    @abstractmethod
    def update_activities(self, activities: List[ActivityData]) -> None:
        pass
