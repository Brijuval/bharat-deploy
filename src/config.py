"""
Configuration Handler for BharatDeploy
Loads bharat.yaml and merges with environment variables
"""

import os
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Default configuration values
DEFAULTS = {
    "groq": {
        "model": "llama3-8b-8192",
        "temperature": 0.1,
        "max_tokens": 1024,
        "max_retries": 3,
        "retry_delay": 1.0,
    },
    "aws": {
        "region": "ap-south-1",  # Mumbai - default for Indian users
        "dry_run": False,
        "timeout": 30,
    },
    "language": {
        "default": "auto",
        "supported": ["hi", "ta", "kn", "en", "hinglish"],
    },
    "safety": {
        "confirm_destructive": True,
        "blocked_commands": ["ec2 terminate-instances", "s3 rb --force", "rds delete-db-instance"],
    },
    "output": {
        "format": "json",
        "verbose": False,
    },
}


class BharatConfig:
    """Configuration manager for BharatDeploy."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to bharat.yaml config file. If None, searches default locations.
        """
        self._config = {}
        self._load_defaults()
        self._load_yaml(config_path)
        self._load_env_vars()

    def _load_defaults(self):
        """Load default configuration values."""
        self._config = _deep_merge({}, DEFAULTS)

    def _load_yaml(self, config_path: Optional[str] = None):
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            return

        # Search for config file in default locations
        search_paths = []
        if config_path:
            search_paths.append(Path(config_path))
        search_paths.extend([
            Path.cwd() / "bharat.yaml",
            Path.cwd() / "config" / "bharat.yaml",
            Path.home() / ".bharat" / "config.yaml",
        ])

        for path in search_paths:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        yaml_config = yaml.safe_load(f)
                    if yaml_config and isinstance(yaml_config, dict):
                        self._config = _deep_merge(self._config, yaml_config)
                except (yaml.YAMLError, OSError):
                    pass
                break

    def _load_env_vars(self):
        """Override configuration with environment variables."""
        env_mappings = {
            "GROQ_API_KEY": ("groq", "api_key"),
            "AWS_REGION": ("aws", "region"),
            "AWS_DEFAULT_REGION": ("aws", "region"),
            "BHARAT_DRY_RUN": ("aws", "dry_run"),
            "BHARAT_LANGUAGE": ("language", "default"),
            "BHARAT_VERBOSE": ("output", "verbose"),
            "BHARAT_GROQ_MODEL": ("groq", "model"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section not in self._config:
                    self._config[section] = {}
                # Handle boolean env vars
                if value.lower() in ("true", "1", "yes"):
                    value = True
                elif value.lower() in ("false", "0", "no"):
                    value = False
                self._config[section][key] = value

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.

        Args:
            *keys: Key path (e.g., "groq", "model")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        current = self._config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_groq_api_key(self) -> Optional[str]:
        """Get the Groq API key."""
        return self.get("groq", "api_key") or os.environ.get("GROQ_API_KEY")

    def get_aws_region(self) -> str:
        """Get the AWS region."""
        return self.get("aws", "region") or "ap-south-1"

    def is_dry_run(self) -> bool:
        """Check if dry-run mode is enabled."""
        return bool(self.get("aws", "dry_run", default=False))

    def get_groq_model(self) -> str:
        """Get the Groq model name."""
        return self.get("groq", "model") or "llama3-8b-8192"

    def get_default_language(self) -> str:
        """Get the default language setting."""
        return self.get("language", "default") or "auto"

    def should_confirm_destructive(self) -> bool:
        """Check if destructive operations need confirmation."""
        return bool(self.get("safety", "confirm_destructive", default=True))

    def to_dict(self) -> dict:
        """Return the full configuration as a dictionary."""
        return dict(self._config)


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary with override values

    Returns:
        Merged dictionary
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Global config instance
_config_instance: Optional[BharatConfig] = None


def get_config(config_path: Optional[str] = None) -> BharatConfig:
    """
    Get or create the global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        BharatConfig instance
    """
    global _config_instance
    if _config_instance is None or config_path is not None:
        _config_instance = BharatConfig(config_path)
    return _config_instance


def reset_config():
    """Reset the global configuration instance (useful for testing)."""
    global _config_instance
    _config_instance = None
