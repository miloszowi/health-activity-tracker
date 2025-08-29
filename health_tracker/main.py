import click
import logging
from dotenv import load_dotenv
import os
from datetime import date

from health_tracker.destination.activities.activities_target import ActivitiesTarget
from health_tracker.destination.health.health_target import HealthTarget
from health_tracker.provider.activities.activities_source import ActivitiesSource
from health_tracker.provider.health.health_source import HealthSource

from health_tracker.sync_service import SyncService
from health_tracker.utils.click_styling import info, error, success, warn, step

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE_PATH', '/var/log/health-activity-tracker.log'))
    ]
)


@click.group()
def cli():
    """Health Activity Tracker - Sync data from Garmin and Strava to Google Sheets"""
    pass


@cli.command("sync-health")
@click.option(
    "--source",
    type=click.Choice(HealthSource.choices(), case_sensitive=False),
    default=HealthSource.GARMIN.label,
    show_default=True,
    help=HealthSource.help(),
)
@click.option(
    "--target",
    type=click.Choice(HealthTarget.choices(), case_sensitive=False),
    default=HealthTarget.SHEETS.label,
    show_default=True,
    help=HealthTarget.help(),
)
@click.option("--start-date", help="Start date (YYYY-MM-DD)", default=date.today())
@click.option("--end-date", help="End date (YYYY-MM-DD)", default=date.today())
def sync_health(source: str, target: str, start_date: str, end_date: str):
    """📊 Sync health metrics (sleep, HRV, stress, etc.)"""
    service = SyncService()
    health_source = HealthSource.from_label(source)
    health_target = HealthTarget.from_label(target)

    info(f"Starting health sync from {health_source.label} to {health_target.label} ({start_date} → {end_date})")

    try:
        service.sync_health(health_source, health_target, start_date, end_date)
        success(f"Health sync from {health_source.label} to {health_target.label} completed successfully ✅")
    except Exception as e:
        error(f"Health sync failed: {e}")


@cli.command("sync-activities")
@click.option(
    "--source",
    type=click.Choice(ActivitiesSource.choices(), case_sensitive=False),
    default=ActivitiesSource.STRAVA.label,
    show_default=True,
    help=ActivitiesSource.help(),
)
@click.option(
    "--target",
    type=click.Choice(HealthTarget.choices(), case_sensitive=False),
    default=HealthTarget.SHEETS.label,
    show_default=True,
    help=HealthTarget.help(),
)
@click.option("--minutes-ago", type=int, default=360, show_default=True,
              help="Fetch activities from last X minutes")
def sync_activities(source: str, target: str, minutes_ago: int):
    """🏃 Sync recent activities (runs, rides, workouts, …)"""
    service = SyncService()
    activities_source = ActivitiesSource.from_label(source)
    activities_target = ActivitiesTarget.from_label(target)

    info(f"Starting activities sync from {activities_source.label} to {activities_target.label} (last {minutes_ago} minutes)")
    try:
        service.sync_activities(activities_source, activities_target, minutes_ago=minutes_ago)
        success(f"Activities sync from {activities_source.label} to {activities_target.label} completed successfully ✅")
    except Exception as e:
        error(f"Activities sync failed: {e}")


if __name__ == "__main__":
    cli()
