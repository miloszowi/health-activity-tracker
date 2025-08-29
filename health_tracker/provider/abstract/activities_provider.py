from abc import ABC, abstractmethod
from typing import List
from health_tracker.data.activity_data import ActivityData


class ActivitiesProvider(ABC):
    @abstractmethod
    def fetch_recent_activities(self, minutes_ago: int = 360) -> List[ActivityData]:
        pass
