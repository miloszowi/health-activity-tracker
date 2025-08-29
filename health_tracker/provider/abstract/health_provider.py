from abc import ABC, abstractmethod
from health_tracker.data.day_health_data import DayHealthData


class HealthProvider(ABC):
    @abstractmethod
    def get_data_for_date(self, date: str) -> DayHealthData:
        pass
