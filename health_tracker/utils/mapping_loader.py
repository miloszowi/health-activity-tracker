import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

from health_tracker.data.activity_data import ActivityData
from health_tracker.data.day_health_data import DayHealthData


class DataType(Enum):
    ACTIVITY = "activity"
    HEALTH = "health"


class TargetType(Enum):
    SHEETS = "sheets"
    NOTION = "notion"


class MappingLoader:
    """Loads mappings for different targets and data types with fallback support"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.default_mappings_path = self.project_root / "health_tracker" / "config" / "defaults" / "mapping"
        self.local_config_path = self.project_root / "config" / "mapping"
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for pyproject.toml or setup.py"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists() or (current / "setup.py").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def load_mapping(self, target_type: TargetType, data_type: DataType) -> Dict[str, Any]:
        """
        Load mapping for a specific target and data type.
        First checks local config, then falls back to defaults.
        
        Args:
            target_type: Type of target (sheets, notion)
            data_type: Type of data (activity, health)
            
        Returns:
            Dictionary with mapping configuration
            
        Raises:
            FileNotFoundError: If no mapping file is found
        """
        local_mapping = self._load_from_path(
            self.local_config_path / data_type.value / f"{target_type.value}.yaml"
        )
        if local_mapping:
            return local_mapping
        
        default_mapping = self._load_from_path(
            self.default_mappings_path / data_type.value / f"{target_type.value}.yaml"
        )
        if default_mapping:
            return default_mapping
        
        raise FileNotFoundError(
            f"No mapping found for target '{target_type.value}' and data type '{data_type.value}'"
        )
    
    def _load_from_path(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file from given path if it exists"""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load mapping from {file_path}: {e}")
            return None
    
    def get_available_mappings(self) -> Dict[str, Dict[str, list]]:
        """Get list of all available mappings for documentation purposes"""
        available = {}
        
        for target_type in TargetType:
            available[target_type.value] = {}
            for data_type in DataType:
                mappings = []
                
                local_path = self.local_config_path / data_type.value / f"{target_type.value}.yaml"
                if local_path.exists():
                    mappings.append(f"local:config/mapping/{data_type.value}/{target_type.value}.yaml")
                
                default_path = self.default_mappings_path / data_type.value / f"{target_type.value}.yaml"
                if default_path.exists():
                    mappings.append(f"default:health_tracker/config/defaults/mapping/{data_type.value}/{target_type.value}.yaml")
                
                available[target_type.value][data_type.value] = mappings
        
        return available
    
    def create_local_config_structure(self):
        """Create local config directory structure with example files"""
        if not self.local_config_path.exists():
            self.local_config_path.mkdir(parents=True, exist_ok=True)
        
        activity_config_path = self.local_config_path / "activity"
        activity_config_path.mkdir(exist_ok=True)
        
        health_config_path = self.local_config_path / "health"
        health_config_path.mkdir(exist_ok=True)
        
        print(f"Created local config structure at: {self.local_config_path}")
        print("You can now copy and customize mapping files from defaults directory")


def load_activity_mapping(target_type: TargetType) -> Dict[str, Any]:
    """Load mapping for activities to a specific target"""
    loader = MappingLoader()
    return loader.load_mapping(target_type, DataType.ACTIVITY)


def load_health_mapping(target_type: TargetType) -> Dict[str, Any]:
    """Load mapping for health data to a specific target"""
    loader = MappingLoader()
    return loader.load_mapping(target_type, DataType.HEALTH)


def get_mapping_info() -> Dict[str, Dict[str, list]]:
    """Get information about all available mappings"""
    loader = MappingLoader()
    return loader.get_available_mappings()