import logging
import os
import garth
import garminconnect
from typing import Optional, Union
from health_tracker.data.day_health_data import DayHealthData
from health_tracker.provider.abstract.health_provider import HealthProvider
from health_tracker.utils.config_loader import config_get_path


class GarminHealthProvider(HealthProvider):
    def __init__(self):
        self.logger = logging.getLogger("health-tracker")
        self._setup_auth()

    def _setup_auth(self):
        """Setup Garmin authentication"""
        garmin_token_dir = config_get_path('garmin.token_dir', env_key='GARMIN_TOKEN_FILE_PATH')
        if not garmin_token_dir:
            raise ValueError("Missing Garmin token directory path. Set GARMIN_TOKEN_FILE_PATH env var or configure in config.yaml")
        
        garmin_oauth_token_path = garmin_token_dir / "oauth2_token.json"

        if not garmin_oauth_token_path.exists():
            garth.login(os.environ.get("GARMIN_EMAIL"), os.environ.get("GARMIN_PASSWORD"))
            garth.save(str(garmin_token_dir))

        self.garmin = garminconnect.Garmin()
        self.garmin.login(tokenstore=str(garmin_token_dir))

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
                sleep_hours=self._secs_to_hours(sleep_dto.get("sleepTimeSeconds")),
                sleep_score=self._safe_round(sleep_dto.get("sleepScores", {}).get("overall", {}).get("value")),
                sleep_deep_hours=self._secs_to_hours(sleep_dto.get("deepSleepSeconds")),
                sleep_rem_hours=self._secs_to_hours(sleep_dto.get("remSleepSeconds")),
                sleep_awake_minutes=self._secs_to_minutes(sleep_dto.get("awakeSleepSeconds")),
                sleep_awake_count=sleep_dto.get("awakeCount"),
                average_sleep_stress=self._safe_round(sleep_dto.get("avgSleepStress")),
                sleep_needed_hours=self._secs_to_minutes(sleep_dto.get("sleepNeed", {}).get("actual")),
                average_spo2_value=self._safe_round(sleep_dto.get("averageSpO2Value")),
                average_overnight_hrv=self._safe_round(sleep_data.get("avgOvernightHrv")),
                resting_heart_rate=sleep_data.get("restingHeartRate"),
                average_stress_level=avg_stress,
                stress_hours=self._secs_to_hours(data.get("stressDuration")),
                weight=self._safe_round(data.get("weight"), 1000),
                body_battery=data.get("bodyBatteryAtWakeTime"),
                run_vo2max=self._safe_round(self._safe_get_vo2max(max_metrics, "generic")),
                bike_vo2max=self._safe_round(self._safe_get_vo2max(max_metrics, "cycling")),
                bike_ftp=self._get_ftp_for_date(date),
                total_steps=data.get("totalSteps"),
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
