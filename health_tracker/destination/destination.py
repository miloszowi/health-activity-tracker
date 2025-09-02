from typing import List
from enum import Enum
from functools import cached_property

from health_tracker.data.day_health_data import DayHealthData
from health_tracker.data.activity_data import ActivityData
from health_tracker.destination.google_sheets import GoogleSheets
from health_tracker.destination.notion import Notion
from health_tracker.utils.mapping_loader import MappingLoader, TargetType as MappingTargetType, DataType


class TargetType(Enum):
    SHEETS = "sheets"
    NOTION = "notion"


class Target:
    def __init__(self, target_type: TargetType):
        self.target_type = target_type
        self._instance = None
        self._mapping_loader = MappingLoader()

    @cached_property
    def instance(self):
        if self.target_type == TargetType.SHEETS:
            return GoogleSheets()
        elif self.target_type == TargetType.NOTION:
            return Notion()
        else:
            raise ValueError(f"Unknown target type: {self.target_type}")

    @property
    def label(self) -> str:
        return self.target_type.value

    def get_activity_mapping(self) -> dict:
        """Get mapping configuration for activities"""
        mapping_target = MappingTargetType(self.target_type.value)
        return self._mapping_loader.load_mapping(mapping_target, DataType.ACTIVITY)

    def get_health_mapping(self) -> dict:
        """Get mapping configuration for health data"""
        mapping_target = MappingTargetType(self.target_type.value)
        return self._mapping_loader.load_mapping(mapping_target, DataType.HEALTH)

    def update_health_data(self, date: str, data: DayHealthData) -> None:
        """Update health data for a specific date"""
        self.instance.update_health_data(date, data)

    def update_activities(self, activities: List[ActivityData]) -> None:
        """Update activities data"""
        self.instance.update_activities(activities)

    @classmethod
    def from_label(cls, label: str) -> "Target":
        """Create a Target instance from a label string"""
        try:
            target_type = TargetType(label.lower())
            return cls(target_type)
        except ValueError:
            raise ValueError(f"{label} is not a valid target. Available targets: {', '.join([t.value for t in TargetType])}")

    @classmethod
    def choices(cls) -> List[str]:
        """Get list of available target labels"""
        return [t.value for t in TargetType]

    @classmethod
    def help(cls) -> str:
        """Get help text for available targets"""
        return f"Available targets: {', '.join(cls.choices())}"

    @classmethod
    def get_mapping_info(cls) -> dict:
        """Get information about available mappings for all targets"""
        loader = MappingLoader()
        return loader.get_available_mappings()

    @classmethod
    def setup_local_config(cls):
        """Set up local configuration structure for customizing mappings"""
        loader = MappingLoader()
        loader.create_local_config_structure()
        
        from health_tracker.utils.config_loader import get_config
        config = get_config()
        config.create_local_config_structure()
