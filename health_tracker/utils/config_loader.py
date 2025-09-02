import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import lru_cache


class ConfigLoader:
    """Loads configuration from YAML files and environment variables with fallback support"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.default_config_path = self.project_root / "health_tracker" / "config" / "config.yaml"
        self.local_config_path = self.project_root / "config" / "config.yaml"
        
        self._default_config = self._load_yaml(self.default_config_path) or {}
        self._local_config = self._load_yaml(self.local_config_path) or {}
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for pyproject.toml or setup.py"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists() or (current / "setup.py").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file from given path if it exists"""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {file_path}: {e}")
            return None
    
    def get(self, key: str, default: Any = None, env_key: Optional[str] = None) -> Any:
        """
        Get configuration value with fallback priority:
        1. Environment variable (if env_key provided)
        2. Local config (config/config.yaml)
        3. Default config (health_tracker/config/config.yaml)
        4. Default value
        
        Args:
            key: Dot-notation key (e.g., 'google_sheets.spreadsheet_url')
            default: Default value if nothing found
            env_key: Environment variable name to check first
            
        Returns:
            Configuration value
        """
        if env_key:
            env_value = os.environ.get(env_key)
            if env_value is not None:
                return env_value
        
        local_value = self._get_nested(self._local_config, key)
        if local_value is not None:
            return local_value
        
        default_value = self._get_nested(self._default_config, key)
        if default_value is not None:
            return default_value
        
        return default
    
    def _get_nested(self, config: Dict[str, Any], key: str) -> Any:
        """Get nested value from config using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def get_path(self, key: str, default: Any = None, env_key: Optional[str] = None) -> Path:
        """Get configuration value as Path object"""
        value = self.get(key, default, env_key)
        if value is None:
            return None
        
        path = Path(value)
        if not path.is_absolute():
            path = self.project_root / path
        
        return path
    
    def get_int(self, key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[int]:
        """Get configuration value as integer"""
        value = self.get(key, default, env_key)
        if value is None:
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[float]:
        """Get configuration value as float"""
        value = self.get(key, default, env_key)
        if value is None:
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[bool]:
        """Get configuration value as boolean"""
        value = self.get(key, default, env_key)
        if value is None:
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)
    
    def create_local_config_structure(self):
        """Create local config directory and copy default config"""
        local_config_dir = self.local_config_path.parent
        local_config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.local_config_path.exists() and self.default_config_path.exists():
            import shutil
            shutil.copy2(self.default_config_path, self.local_config_path)
            print(f"Copied default config to: {self.local_config_path}")
            print("Please edit this file with your specific configuration")
        
        print(f"Local config structure ready at: {local_config_dir}")
    
    def reload(self):
        """Reload configuration files"""
        self._default_config = self._load_yaml(self.default_config_path) or {}
        self._local_config = self._load_yaml(self.local_config_path) or {}


@lru_cache(maxsize=1)
def get_config() -> ConfigLoader:
    """Get global configuration instance"""
    return ConfigLoader()


def config_get(key: str, default: Any = None, env_key: Optional[str] = None) -> Any:
    """Get configuration value"""
    return get_config().get(key, default, env_key)


def config_get_path(key: str, default: Any = None, env_key: Optional[str] = None) -> Path:
    """Get configuration value as Path"""
    return get_config().get_path(key, default, env_key)


def config_get_int(key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[int]:
    """Get configuration value as integer"""
    return get_config().get_int(key, default, env_key)


def config_get_float(key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[float]:
    """Get configuration value as float"""
    return get_config().get_float(key, default, env_key)


def config_get_bool(key: str, default: Any = None, env_key: Optional[str] = None) -> Optional[bool]:
    """Get configuration value as boolean"""
    return get_config().get_bool(key, default, env_key) 