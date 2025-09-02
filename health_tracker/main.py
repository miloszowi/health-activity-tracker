from datetime import date, timedelta, datetime
import sys

import click
import logging
from dotenv import load_dotenv

from health_tracker.destination.destination import Target
from health_tracker.provider.activities.activities_source import ActivitiesSource
from health_tracker.provider.health.health_source import HealthSource
from health_tracker.utils.config_loader import config_get, config_get_path, config_get_int

from health_tracker.sync_service import SyncService
from health_tracker.utils.click_styling import info, error, success, warn, step

load_dotenv()

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

log_file_path = config_get_path('logging.file_path', '/var/log/health-activity-tracker.log')
file_handler = logging.FileHandler(log_file_path, mode="a")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


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
    type=click.Choice(Target.choices(), case_sensitive=False),
    default=Target.from_label("sheets").label,
    show_default=True,
    help=Target.help(),
)
@click.option("--start-date", help="Start date (YYYY-MM-DD)", default=date.today())
@click.option("--end-date", help="End date (YYYY-MM-DD)", default=date.today())
def sync_health(source: str, target: str, start_date: str, end_date: str):
    """📊 Sync health metrics (sleep, HRV, stress, etc.)"""
    service = SyncService()
    health_source = HealthSource.from_label(source)
    health_target = Target.from_label(target)

    info(f"Starting health sync from {health_source.label} to {health_target.label} ({start_date} → {end_date})")

    try:
        service.sync_health(
            source=health_source,
            target=health_target,
            start_date=start_date,
            end_date=end_date
        )
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
    type=click.Choice(Target.choices(), case_sensitive=False),
    default=Target.from_label("sheets").label,
    show_default=True,
    help=Target.help(),
)
@click.option("--start-date",
              default=(datetime.today() - timedelta(hours=12, minutes=0)).strftime("%Y-%m-%d %H:%M:%S"),
              show_default=True,
              type=str,
              required=True,
              help="Start date for activities (format: YYYY-MM-DD HH:MM:SS)"
)
@click.option("--end-date",
              default=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
              show_default=True,
              type=str,
              required=True,
              help="End date for activities (format: YYYY-MM-DD HH:MM:SS)"
  )
def sync_activities(source: str, target: str, start_date: str, end_date: str):
    """🏃 Sync recent activities (runs, rides, workouts, …)"""
    service = SyncService()
    activities_source = ActivitiesSource.from_label(source)
    activities_target = Target.from_label(target)

    info(f"Starting activities sync from {activities_source.label} to {activities_target.label} (range: {start_date} to {end_date})")
    try:
        service.sync_activities(
            source=activities_source,
            target=activities_target,
            start_date=start_date,
            end_date=end_date
        )
        success(f"Activities sync from {activities_source.label} to {activities_target.label} completed successfully ✅")
    except Exception as e:
        error(f"Activities sync failed: {e}")


@cli.command("setup-config")
def setup_config():
    """🔧 Set up local configuration structure for customizing mappings"""
    try:
        Target.setup_local_config()
        success("Local configuration structure created successfully! ✅")
        info("You can now customize mapping files in the config/mapping/ directory")
        info("These files will not be committed to git and will override defaults")
    except Exception as e:
        error(f"Failed to set up configuration: {e}")


@cli.command("setup-main-config")
def setup_main_config():
    """⚙️ Set up main configuration file for customizing paths and settings"""
    try:
        from health_tracker.utils.config_loader import get_config
        config = get_config()
        config.create_local_config_structure()
        success("Main configuration structure created successfully! ✅")
        info("You can now customize the main config.yaml file in the config/ directory")
        info("This file will not be committed to git and will override defaults")
    except Exception as e:
        error(f"Failed to set up main configuration: {e}")


@cli.command("mapping-info")
def mapping_info():
    """📋 Show information about available mappings"""
    try:
        mappings = Target.get_mapping_info()
        info("Available mappings:")
        for target, data_types in mappings.items():
            print(f"\n  {target.upper()}:")
            for data_type, files in data_types.items():
                print(f"    {data_type}:")
                for file_path in files:
                    print(f"      - {file_path}")
    except Exception as e:
        error(f"Failed to get mapping info: {e}")


@cli.command("config-info")
def config_info():
    """🔍 Show current configuration values"""
    try:
        from health_tracker.utils.config_loader import get_config
        config = get_config()
        
        info("Current configuration values:")
        print("\n  Logging:")
        print(f"    File path: {config.get('logging.file_path')}")
        print(f"    Level: {config.get('logging.level')}")
        
        print("\n  Google Sheets:")
        print(f"    Credentials file: {config.get_path('google_sheets.credentials_file')}")
        print(f"    Spreadsheet URL: {config.get('google_sheets.spreadsheet_url')}")
        print(f"    Health worksheet: {config.get('google_sheets.worksheets.health')}")
        print(f"    Activities worksheet: {config.get('google_sheets.worksheets.activities')}")
        
        print("\n  Notion:")
        print(f"    Health database: {config.get('notion.databases.health')}")
        print(f"    Activities database: {config.get('notion.databases.activities')}")
        
        print("\n  Garmin:")
        print(f"    Token directory: {config.get_path('garmin.token_dir')}")
        
        print("\n  Strava:")
        print(f"    Token file: {config.get_path('strava.token_file')}")
        print(f"    Processed file: {config.get_path('strava.processed_file')}")
        
        print("\n  Data:")
        print(f"    Date format: {config.get('data.date_format')}")
        print(f"    Datetime format: {config.get('data.datetime_format')}")
        
    except Exception as e:
        error(f"Failed to get config info: {e}")


if __name__ == "__main__":
    cli()
