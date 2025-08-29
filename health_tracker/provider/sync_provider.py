from abc import ABC, abstractmethod
from typing import Optional


class SyncProvider(ABC):
    @abstractmethod
    def sync(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
             minutes_ago: Optional[int] = None) -> None:
        pass
