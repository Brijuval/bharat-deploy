"""
Configuration Handler for BharatDeploy.

Loads settings from environment variables and an optional YAML config file.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class Config:
    """Central configuration object for BharatDeploy.

    Priority (highest to lowest):
    1. Environment variables
    2. YAML config file (``config/bharat.yaml`` or custom path)
    3. Built-in defaults
    """

    DEFAULTS: Dict[str, Any] = {
        "groq_model": "llama3-8b-8192",
        "default_language": "hi",
        "log_level": "INFO",
        "dry_run": False,
        "aws_region": "ap-south-1",
        "max_retries": 3,
        "retry_delay": 1.0,
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        self._data: Dict[str, Any] = dict(self.DEFAULTS)
        self._load_dotenv()
        self._load_yaml(config_path)
        self._load_env_vars()

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------

    def _load_dotenv(self) -> None:
        """Load .env file if present (silently skip if missing)."""
        try:
            from dotenv import load_dotenv

            load_dotenv(override=False)
        except ImportError:
            pass

    def _load_yaml(self, config_path: Optional[str]) -> None:
        """Load YAML config file."""
        paths_to_try = []
        if config_path:
            paths_to_try.append(Path(config_path))
        paths_to_try += [
            Path("config/bharat.yaml"),
            Path("bharat.yaml"),
        ]

        for path in paths_to_try:
            if path.exists():
                try:
                    with path.open() as f:
                        data = yaml.safe_load(f) or {}
                    self._data.update(data)
                    logger.debug("Loaded config from %s", path)
                except Exception as exc:
                    logger.warning("Failed to load config %s: %s", path, exc)
                break

    def _load_env_vars(self) -> None:
        """Override settings from environment variables."""
        mapping = {
            "GROQ_API_KEY": "groq_api_key",
            "GROQ_MODEL": "groq_model",
            "AWS_ACCESS_KEY_ID": "aws_access_key_id",
            "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
            "AWS_DEFAULT_REGION": "aws_region",
            "BHARAT_DEFAULT_LANGUAGE": "default_language",
            "BHARAT_LOG_LEVEL": "log_level",
            "BHARAT_DRY_RUN": "dry_run",
        }
        for env_key, cfg_key in mapping.items():
            val = os.environ.get(env_key)
            if val is not None:
                # Coerce boolean strings
                if cfg_key == "dry_run":
                    self._data[cfg_key] = val.lower() in ("1", "true", "yes")
                else:
                    self._data[cfg_key] = val

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if not found."""
        return self._data.get(key, default)

    @property
    def groq_api_key(self) -> Optional[str]:
        return self._data.get("groq_api_key")

    @property
    def groq_model(self) -> str:
        return self._data.get("groq_model", self.DEFAULTS["groq_model"])

    @property
    def aws_region(self) -> str:
        return self._data.get("aws_region", self.DEFAULTS["aws_region"])

    @property
    def default_language(self) -> str:
        return self._data.get("default_language", self.DEFAULTS["default_language"])

    @property
    def dry_run(self) -> bool:
        return bool(self._data.get("dry_run", False))

    @property
    def log_level(self) -> str:
        return self._data.get("log_level", self.DEFAULTS["log_level"])

    @property
    def max_retries(self) -> int:
        return int(self._data.get("max_retries", self.DEFAULTS["max_retries"]))

    @property
    def retry_delay(self) -> float:
        return float(self._data.get("retry_delay", self.DEFAULTS["retry_delay"]))
