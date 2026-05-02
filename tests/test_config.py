"""
Tests for src/config.py
"""

import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

from src.config import Config


class TestConfig:

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------

    def test_default_groq_model(self):
        with patch.dict(os.environ, {}, clear=False):
            cfg = Config()
        assert cfg.groq_model == "llama3-8b-8192"

    def test_default_aws_region(self):
        cfg = Config()
        assert cfg.aws_region == "ap-south-1"

    def test_default_language(self):
        cfg = Config()
        assert cfg.default_language == "hi"

    def test_default_dry_run_is_false(self):
        cfg = Config()
        assert cfg.dry_run is False

    def test_default_max_retries(self):
        cfg = Config()
        assert cfg.max_retries == 3

    # ------------------------------------------------------------------
    # Environment variable overrides
    # ------------------------------------------------------------------

    def test_groq_api_key_from_env(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key-123"}):
            cfg = Config()
        assert cfg.groq_api_key == "test-key-123"

    def test_groq_model_from_env(self):
        with patch.dict(os.environ, {"GROQ_MODEL": "llama3-70b-8192"}):
            cfg = Config()
        assert cfg.groq_model == "llama3-70b-8192"

    def test_aws_region_from_env(self):
        with patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}):
            cfg = Config()
        assert cfg.aws_region == "us-east-1"

    def test_dry_run_true_from_env_string(self):
        with patch.dict(os.environ, {"BHARAT_DRY_RUN": "true"}):
            cfg = Config()
        assert cfg.dry_run is True

    def test_dry_run_false_from_env_string(self):
        with patch.dict(os.environ, {"BHARAT_DRY_RUN": "false"}):
            cfg = Config()
        assert cfg.dry_run is False

    def test_dry_run_1_from_env(self):
        with patch.dict(os.environ, {"BHARAT_DRY_RUN": "1"}):
            cfg = Config()
        assert cfg.dry_run is True

    def test_default_language_from_env(self):
        with patch.dict(os.environ, {"BHARAT_DEFAULT_LANGUAGE": "en"}):
            cfg = Config()
        assert cfg.default_language == "en"

    # ------------------------------------------------------------------
    # .get() method
    # ------------------------------------------------------------------

    def test_get_existing_key(self):
        cfg = Config()
        assert cfg.get("groq_model") == cfg.groq_model

    def test_get_missing_key_returns_default(self):
        cfg = Config()
        assert cfg.get("nonexistent_key", "fallback") == "fallback"

    def test_get_missing_key_returns_none_by_default(self):
        cfg = Config()
        assert cfg.get("nonexistent_key") is None

    # ------------------------------------------------------------------
    # YAML loading
    # ------------------------------------------------------------------

    def test_yaml_config_loaded(self, tmp_path):
        yaml_content = "groq_model: llama3-70b-8192\naws_region: eu-west-1\n"
        config_file = tmp_path / "bharat.yaml"
        config_file.write_text(yaml_content)

        cfg = Config(config_path=str(config_file))
        assert cfg.groq_model == "llama3-70b-8192"
        assert cfg.aws_region == "eu-west-1"

    def test_env_overrides_yaml(self, tmp_path):
        yaml_content = "groq_model: llama3-70b-8192\n"
        config_file = tmp_path / "bharat.yaml"
        config_file.write_text(yaml_content)

        with patch.dict(os.environ, {"GROQ_MODEL": "llama3-8b-8192"}):
            cfg = Config(config_path=str(config_file))
        # Env var should win
        assert cfg.groq_model == "llama3-8b-8192"
