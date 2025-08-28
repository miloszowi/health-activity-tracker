from garminconnect import Garmin
from dataclasses import dataclass
from typing import Optional
import pandas as pd
from datetime import date
import json

garmin = Garmin()
garmin.login('~/.garminconnect')

@dataclass()
class SyncGarminData:
    sleepHours: Optional[float]
    sleepScore: Optional[int]
    restingHeartRate: Optional[int]
    averageHRV: Optional[int]
    weight: Optional[int]
    bodyBattery: Optional[int]
    runVO2max: Optional[int]
    bikeVO2max: Optional[int]
    bikeFTP: Optional[int]

def get_for_date(date: str) -> SyncGarminData:
    data = garmin.get_stats_and_body(cdate=date)
    sleep_data = garmin.get_sleep_data(cdate=date)
    if sleep_data and 'dailySleepDTO' in sleep_data:
        daily_sleep = sleep_data['dailySleepDTO']
        print("dailySleepDTO keys:")
        print(daily_sleep.keys())

        # Print the full structure
        print("\nFull dailySleepDTO structure:")
        print(json.dumps(daily_sleep, indent=2, default=str))
    sleepHours = round(data.get('sleepingSeconds') / 60 / 60, 2)
    # sync = SyncGarminData(
    #     sleepHours=data.get('')
    # )

dates = pd.date_range(start='2025-08-20', end='2025-08-20', freq='D').strftime('%Y-%m-%d').tolist()

for date in dates:
    garmin_data = get_for_date(date)




