from abc import ABC, abstractmethod
from typing import Any, Dict

from health_tracker.data.activity_data import ActivityData


class AbstractActivityMapper(ABC):
    @abstractmethod
    def map(self, activity: ActivityData) -> Dict[str, Any]:
        pass