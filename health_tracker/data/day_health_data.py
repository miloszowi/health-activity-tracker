from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime


@dataclass
class DayHealthData:
    date: Union[datetime, str]
    sleepHours: Optional[float]
    sleepScore: Optional[int]
    sleepDeepHours: Optional[float]
    sleepRemHours: Optional[float]
    sleepAwakeMinutes: Optional[float]
    sleepAwakeCount: Optional[int]
    averageSleepStress: Optional[float]
    sleepNeededHours: Optional[float]
    averageSpO2Value: Optional[float]
    averageOvernightHrv: Optional[float]
    restingHeartRate: Optional[int]
    averageStressLevel: Optional[int]
    stressHours: Optional[float]
    weight: Optional[int]
    bodyBattery: Optional[int]
    runVO2max: Optional[int]
    bikeVO2max: Optional[int]
    bikeFTP: Optional[int]
    totalSteps: Optional[int]
