import logging
import os
import garth
import garminconnect
from typing import Optional, Union
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.provider.abstract.health_provider import HealthProvider


class GarminHealthProvider(HealthProvider):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_auth()

    def _setup_auth(self):
        """Setup Garmin authentication"""
        garmin_token_store = os.getenv("GARMIN_TOKEN_FILE_PATH")
        garmin_oauth_token_path = f"{garmin_token_store}/oauth2_token.json"

        if not os.path.exists(garmin_oauth_token_path):
            garth.login(os.environ.get("GARMIN_EMAIL"), os.environ.get("GARMIN_PASSWORD"))
            garth.save(garmin_token_store)

        self.garmin = garminconnect.Garmin()
        self.garmin.login(tokenstore=garmin_token_store)

    def get_data_for_date(self, date: str) -> DayHealthData:
        """Get all Garmin data for a specific date"""
        try:
            data = self.garmin.get_stats_and_body(cdate=date)
            sleep_data = self.garmin.get_sleep_data(cdate=date)
            sleep_dto = sleep_data.get("dailySleepDTO", {})
            max_metrics = self.garmin.get_max_metrics(cdate=date) or {}

            avg_stress = data.get("averageStressLevel") if data.get("averageStressLevel", -1) >= 0 else None

            return DayHealthData(
                date=date,
                sleepHours=self._secs_to_hours(sleep_dto.get("sleepTimeSeconds")),
                sleepScore=self._safe_round(sleep_dto.get("sleepScores", {}).get("overall", {}).get("value")),
                sleepDeepHours=self._secs_to_hours(sleep_dto.get("deepSleepSeconds")),
                sleepRemHours=self._secs_to_hours(sleep_dto.get("remSleepSeconds")),
                sleepAwakeMinutes=self._secs_to_minutes(sleep_dto.get("awakeSleepSeconds")),
                sleepAwakeCount=sleep_dto.get("awakeCount"),
                averageSleepStress=self._safe_round(sleep_dto.get("avgSleepStress")),
                sleepNeededHours=self._secs_to_minutes(sleep_dto.get("sleepNeed", {}).get("actual")),
                averageSpO2Value=self._safe_round(sleep_dto.get("averageSpO2Value")),
                averageOvernightHrv=self._safe_round(sleep_data.get("avgOvernightHrv")),
                restingHeartRate=sleep_data.get("restingHeartRate"),
                averageStressLevel=avg_stress,
                stressHours=self._secs_to_hours(data.get("stressDuration")),
                weight=self._safe_round(data.get("weight"), 1000),
                bodyBattery=data.get("bodyBatteryAtWakeTime"),
                runVO2max=self._safe_round(self._safe_get_vo2max(max_metrics, "generic")),
                bikeVO2max=self._safe_round(self._safe_get_vo2max(max_metrics, "cycling")),
                bikeFTP=self._get_ftp_for_date(date),
                totalSteps=data.get("totalSteps"),
            )
        except Exception as e:
            self.logger.error(f"Error getting Garmin data for {date}: {e}")
            raise

    def _get_ftp_for_date(self, date: str) -> Optional[float]:
        try:
            activities = self.garmin.get_activities_by_date(date, date)
            cycling = [a for a in activities if "cycling" in str(a.get("activityType", "")).lower()]
            for act in cycling:
                details = self.garmin.get_activity(act["activityId"])
                ftp = details.get("summaryDTO", {}).get("functionalThresholdPower")
                if ftp:
                    return ftp
            return None
        except Exception:
            return None

    def _safe_get_vo2max(self, max_metrics, category) -> Optional[float]:
        if not max_metrics or not isinstance(max_metrics, dict):
            return None
        cat_data = max_metrics.get(category)
        if not cat_data or not isinstance(cat_data, dict):
            return None
        return cat_data.get("vo2MaxValue")

    def _secs_to_hours(self, value: Union[float, int, None]) -> Optional[float]:
        if value is None:
            return None
        return round(self._secs_to_minutes(value) / 60, 2)

    def _secs_to_minutes(self, value: Union[float, int, None]) -> Optional[float]:
        if value is None:
            return None
        return round(value / 60, 2)

    def _safe_round(self, value: Union[float, int, None], divider: int = 1, points: int = 2) -> Optional[float]:
        if value is None:
            return None
        return round(value / divider, points)
