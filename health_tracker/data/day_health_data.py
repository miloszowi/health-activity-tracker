from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime


@dataclass
class DayHealthData:
    date: Union[datetime, str]
    sleep_hours: Optional[float]
    sleep_score: Optional[int]
    sleep_deep_hours: Optional[float]
    sleep_rem_hours: Optional[float]
    sleep_awake_minutes: Optional[float]
    sleep_awake_count: Optional[int]
    average_sleep_stress: Optional[float]
    sleep_needed_hours: Optional[float]
    average_spo2_value: Optional[float]
    average_overnight_hrv: Optional[float]
    resting_heart_rate: Optional[int]
    average_stress_level: Optional[int]
    stress_hours: Optional[float]
    weight: Optional[int]
    body_battery: Optional[int]
    run_vo2max: Optional[int]
    bike_vo2max: Optional[int]
    bike_ftp: Optional[int]
    total_steps: Optional[int]
