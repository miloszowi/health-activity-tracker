import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List
from stravalib import Client
from stravalib.model import SummaryActivity

from health_tracker.data.activity_data import ActivityData
from health_tracker.destination.destination import Target
from health_tracker.provider.abstract.activities_provider import ActivitiesProvider
from health_tracker.utils.config_loader import config_get_path


class StravaActivitiesProvider(ActivitiesProvider):
    def __init__(self, target: Target):
        self.logger = logging.getLogger("health-tracker")
        self.client, self.token_data = self._setup_client()
        self.PROCESSED_FILE = config_get_path('strava.processed_file', 'processed_activities.json')
        super().__init__(target)

    def _setup_client(self):
        try:
            token_file = config_get_path('strava.token_file', 'strava_tokens.json')
            with open(token_file, "r") as f:
                token_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Strava tokens file not found at {token_file}")

        client = Client(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires=token_data["expires_at"],
        )
        return client, token_data

    def fetch_activities_by_date_range(self, start_date: str, end_date: str) -> List[ActivityData]:
        """Fetch activities within a specific date range"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError("Date format must be 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")

        self.logger.info(f"Fetching activities from {start_dt.isoformat()} to {end_dt.isoformat()}")

        summaries_iter = self.client.get_activities(after=start_dt, before=end_dt)

        activities_in_range: List[SummaryActivity] = []
        for s in summaries_iter:
            if start_dt <= s.start_date <= end_dt:
                activities_in_range.append(s)

        processed_ids = self._load_processed_ids()
        new_activities = [s for s in activities_in_range if s.id not in processed_ids]

        activities = [self._convert_to_internal(s) for s in new_activities]

        return activities


    def _convert_to_internal(self, summary: SummaryActivity) -> ActivityData:
        activity = self.client.get_activity(activity_id=summary.id)

        return ActivityData(
            id=str(activity.id),
            date=activity.start_date,
            sport_type=activity.sport_type.root,
            duration_seconds=activity.moving_time,
            distance=activity.distance,
            avg_speed=activity.average_speed,
            avg_hr=activity.average_heartrate,
            max_hr=activity.max_heartrate,
            calories=activity.calories,
            avg_watt=activity.average_watts,
            max_watt=activity.max_watts,
            normalized_power=activity.weighted_average_watts,
            elevation=activity.total_elevation_gain,
            url=f"https://strava.com/activities/{activity.id}"
        )

    def mark_as_processed(self, ids: set):
        try:
            with open(self.PROCESSED_FILE, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        existing = set(data.get(self.target.label, []))
        existing.update(ids)
        data[self.target.label] = list(existing)

        with open(self.PROCESSED_FILE, "w") as f:
            json.dump(data, f)

    def _load_processed_ids(self) -> set:
        try:
            with open(self.PROCESSED_FILE, "r") as f:
                data = json.load(f)
                return set(data.get(self.target.label, []))
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def _save_processed_ids(self, ids: set):
        try:
            with open(self.PROCESSED_FILE, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[self.target.label] = list(ids)

        with open(self.PROCESSED_FILE, "w") as f:
            json.dump(data, f)
