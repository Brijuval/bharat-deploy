"""
Tests for Config Handler module
"""

import os
import pytest
import tempfile
from unittest.mock import patch

from src.config import BharatConfig, get_config, reset_config, _deep_merge, DEFAULTS


class TestBharatConfigDefaults:
    def setup_method(self):
        reset_config()

    def test_default_groq_model(self):
        config = BharatConfig()
        assert config.get_groq_model() == "llama3-8b-8192"

    def test_default_aws_region(self):
        config = BharatConfig()
        # Default should be Mumbai for Indian users
        assert config.get_aws_region() == "ap-south-1"

    def test_default_dry_run_false(self):
        config = BharatConfig()
        assert config.is_dry_run() is False

    def test_default_language_auto(self):
        config = BharatConfig()
        assert config.get_default_language() == "auto"

    def test_default_confirm_destructive(self):
        config = BharatConfig()
        assert config.should_confirm_destructive() is True


class TestBharatConfigEnvVars:
    def setup_method(self):
        reset_config()

    def test_groq_api_key_from_env(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-api-key-123"}):
            config = BharatConfig()
        assert config.get_groq_api_key() == "test-api-key-123"

    def test_aws_region_from_env(self):
        with patch.dict("os.environ", {"AWS_REGION": "us-east-1"}):
            config = BharatConfig()
        assert config.get_aws_region() == "us-east-1"

    def test_aws_default_region_from_env(self):
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "eu-west-1"}):
            config = BharatConfig()
        assert config.get_aws_region() == "eu-west-1"

    def test_dry_run_from_env_true(self):
        with patch.dict("os.environ", {"BHARAT_DRY_RUN": "true"}):
            config = BharatConfig()
        assert config.is_dry_run() is True

    def test_dry_run_from_env_false(self):
        with patch.dict("os.environ", {"BHARAT_DRY_RUN": "false"}):
            config = BharatConfig()
        assert config.is_dry_run() is False

    def test_language_from_env(self):
        with patch.dict("os.environ", {"BHARAT_LANGUAGE": "hi"}):
            config = BharatConfig()
        assert config.get_default_language() == "hi"

    def test_groq_model_from_env(self):
        with patch.dict("os.environ", {"BHARAT_GROQ_MODEL": "llama3-70b-8192"}):
            config = BharatConfig()
        assert config.get_groq_model() == "llama3-70b-8192"

    def test_boolean_env_var_1_is_true(self):
        with patch.dict("os.environ", {"BHARAT_DRY_RUN": "1"}):
            config = BharatConfig()
        assert config.is_dry_run() is True

    def test_boolean_env_var_0_is_false(self):
        with patch.dict("os.environ", {"BHARAT_DRY_RUN": "0"}):
            config = BharatConfig()
        assert config.is_dry_run() is False

    def test_boolean_env_var_yes_is_true(self):
        with patch.dict("os.environ", {"BHARAT_DRY_RUN": "yes"}):
            config = BharatConfig()
        assert config.is_dry_run() is True


class TestBharatConfigYaml:
    def setup_method(self):
        reset_config()

    def test_load_from_yaml_file(self):
        yaml_content = """
groq:
  model: llama3-70b-8192
aws:
  region: us-west-2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            config = BharatConfig(config_path=tmp_path)
            assert config.get_groq_model() == "llama3-70b-8192"
            assert config.get_aws_region() == "us-west-2"
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_yaml_uses_defaults(self):
        config = BharatConfig(config_path="/nonexistent/path/config.yaml")
        assert config.get_groq_model() == "llama3-8b-8192"

    def test_invalid_yaml_uses_defaults(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            tmp_path = f.name

        try:
            # Should not raise, fall back to defaults
            config = BharatConfig(config_path=tmp_path)
            assert config.get_groq_model() == "llama3-8b-8192"
        finally:
            os.unlink(tmp_path)

    def test_yaml_merged_with_defaults(self):
        yaml_content = """
groq:
  model: llama3-70b-8192
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            config = BharatConfig(config_path=tmp_path)
            # Custom model from YAML
            assert config.get_groq_model() == "llama3-70b-8192"
            # Default region preserved
            assert config.get_aws_region() == "ap-south-1"
        finally:
            os.unlink(tmp_path)


class TestBharatConfigGet:
    def setup_method(self):
        reset_config()

    def test_get_nested_key(self):
        config = BharatConfig()
        model = config.get("groq", "model")
        assert model == "llama3-8b-8192"

    def test_get_missing_key_returns_default(self):
        config = BharatConfig()
        result = config.get("nonexistent", "key", default="fallback")
        assert result == "fallback"

    def test_get_missing_key_returns_none(self):
        config = BharatConfig()
        result = config.get("nonexistent", "key")
        assert result is None

    def test_to_dict_returns_dict(self):
        config = BharatConfig()
        d = config.to_dict()
        assert isinstance(d, dict)
        assert "groq" in d
        assert "aws" in d
        assert "language" in d


class TestDeepMerge:
    def test_basic_merge(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        base = {"groq": {"model": "llama3-8b-8192", "temperature": 0.1}}
        override = {"groq": {"model": "llama3-70b-8192"}}
        result = _deep_merge(base, override)
        assert result["groq"]["model"] == "llama3-70b-8192"
        assert result["groq"]["temperature"] == 0.1

    def test_empty_override(self):
        base = {"a": 1}
        result = _deep_merge(base, {})
        assert result == {"a": 1}

    def test_empty_base(self):
        override = {"b": 2}
        result = _deep_merge({}, override)
        assert result == {"b": 2}

    def test_override_does_not_mutate_base(self):
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        result = _deep_merge(base, override)
        assert "c" not in base["a"]
        assert "c" in result["a"]


class TestGetConfig:
    def setup_method(self):
        reset_config()

    def test_returns_bharat_config(self):
        config = get_config()
        assert isinstance(config, BharatConfig)

    def test_returns_same_instance(self):
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reset_creates_new_instance(self):
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2
