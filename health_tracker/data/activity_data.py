from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime


@dataclass
class ActivityData:
    date: Union[datetime, str]
    sport_type: str
    duration: str
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
    url_source: Optional[str]

    def url_formula(self) -> str:
        return f'=HYPERLINK("{self.url}";"{self.url_source}")'
