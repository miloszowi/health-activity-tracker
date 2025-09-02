from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime


@dataclass
class ActivityData:
    id: str
    date: Union[datetime, str]
    sport_type: str
    duration_seconds: int
    distance: Optional[int]
    avg_speed: Optional[float]
    avg_hr: Optional[int]
    max_hr: Optional[int]
    calories: Optional[int]
    avg_watt: Optional[int]
    max_watt: Optional[int]
    normalized_power: Optional[int]
    elevation: Optional[int]
    url: Optional[str]
