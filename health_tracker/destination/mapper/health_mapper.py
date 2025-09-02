from abc import ABC, abstractmethod
from health_tracker.data.day_health_data import DayHealthData


class HealthMapper(ABC):
    """Abstract base class for health data mappers"""
    
    @abstractmethod
    def map_health(self, data: DayHealthData) -> dict:
        """Map health data to destination-specific format"""
        pass 