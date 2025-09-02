import logging

import pandas as pd


from health_tracker.destination.destination import Target
from health_tracker.provider.activities.activities_source import ActivitiesSource
from health_tracker.provider.health.health_source import HealthSource
from health_tracker.utils.config_loader import config_get_int

from health_tracker.utils.click_styling import info, error, success, step


class SyncService:
    def __init__(self):
        self.logger = logging.getLogger("health-tracker")

    def sync_health(self, source: HealthSource, target: Target, start_date: str, end_date: str):
        provider = source.provider
        dates = pd.date_range(start=start_date, end=end_date, freq="D").strftime("%Y-%m-%d")

        for current_date in dates:
            step(f"→ Processing {current_date} (health from {source.label})...")
            try:
                data = provider.get_data_for_date(current_date)
                target.update_health_data(current_date, data)
                self._log_success(f"{source.label} health synced for {current_date}")
            except Exception as e:
                self._log_error(f"Error syncing {source.label} health for {current_date}: {e}")

    def sync_activities(self, source: ActivitiesSource, target: Target, start_date: str, end_date: str):
        provider = source.provider(target)
        try:
            activities = provider.fetch_activities_by_date_range(start_date, end_date)
            if not activities:
                info(f"No {source.label} activities to sync")
                return

            target.update_activities(activities)
            provider.mark_as_processed({a.id for a in activities})
            self._log_success(f"Synced {len(activities)} {source.label} activities")
        except Exception as e:
            self._log_error(f"Error syncing {source.label} activities: {e}")

    def _log_success(self, msg: str):
        self.logger.info(f"✓ {msg}")
        success(f"✓ {msg}")

    def _log_error(self, msg: str):
        self.logger.error(f"✗ {msg}")
        error(f"✗ {msg}")
