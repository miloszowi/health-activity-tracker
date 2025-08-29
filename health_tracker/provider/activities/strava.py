import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List
from stravalib import Client
from stravalib.model import SummaryActivity

from health_tracker.data.activity_data import ActivityData
from health_tracker.provider.abstract.activities_provider import ActivitiesProvider


class StravaActivitiesProvider(ActivitiesProvider):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client, self.token_data = self._setup_client()
        self.PROCESSED_FILE = "processed_activities.json"

    def _setup_client(self):
        try:
            with open("strava_tokens.json", "r") as f:
                token_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("strava_tokens.json not found")

        client = Client(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires=token_data["expires_at"],
        )
        return client, token_data

    def fetch_recent_activities(self, minutes_ago: int = 360) -> List[ActivityData]:
        now = datetime.now(timezone.utc)
        time_threshold = now - timedelta(minutes=minutes_ago)

        self.logger.info(f"Fetching activities uploaded after {time_threshold.isoformat()}")
        summaries_iter = self.client.get_activities(after=time_threshold - timedelta(hours=1))

        recent: List[SummaryActivity] = []
        for s in summaries_iter:
            if s.start_date >= time_threshold:
                recent.append(s)
            if len(recent) >= 50:
                break

        processed_ids = self._load_processed_ids()
        new_activities = [s for s in recent if s.id not in processed_ids]

        activities = [self._convert_to_internal(s) for s in new_activities]

        processed_ids.update(s.id for s in new_activities)
        self._save_processed_ids(processed_ids)

        return activities


    def _convert_to_internal(self, summary: SummaryActivity) -> ActivityData:
        activity = self.client.get_activity(activity_id=summary.id)

        mapping = {
            "EBikeRide": "Bike", "Hike": "Walk", "Ride": "Bike", "TrailRun": "Run",
            "VirtualRide": "Bike", "VirtualRun": "Run", "Walk": "Walk",
            "WeightTraining": "Exercise", "Workout": "Exercise", "Yoga": "Stretch",
            "Run": "Run", "Swim": "Swim"
        }

        sport_type = mapping.get(activity.sport_type.root, activity.sport_type.root)

        return ActivityData(
            date=activity.start_date,
            sport_type=sport_type,
            duration=f"=TIME(0;0;{activity.moving_time})",
            distance=activity.distance if sport_type not in ["Stretch", "Exercise"] else 0,
            avg_speed=activity.average_speed,
            avg_hr=activity.average_heartrate,
            max_hr=activity.max_heartrate,
            calories=activity.calories,
            avg_watt=activity.average_watts,
            max_watt=activity.max_watts,
            normalized_power=activity.weighted_average_watts,
            elevation=activity.total_elevation_gain,
            url=f"https://strava.com/activities/{activity.id}",
            url_source="Strava"
        )

    def _load_processed_ids(self) -> set:
        try:
            with open(self.PROCESSED_FILE, "r") as f:
                return set(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def _save_processed_ids(self, ids: set):
        with open(self.PROCESSED_FILE, "w") as f:
            json.dump(list(ids), f)
