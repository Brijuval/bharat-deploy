import os
import tempfile

import pytest
import yaml

from src.config import ConfigHandler


@pytest.fixture
def handler():
    return ConfigHandler()


def test_load_default_config_when_file_missing(handler):
    config = handler.load_config("nonexistent_config_path.yaml")
    assert config["cloud_provider"] == "aws"
    assert config["region"] == "ap-south-1"
    assert config["instance_type"] == "t3.micro"


def test_load_config_from_yaml_file(handler):
    custom_config = {
        "cloud_provider": "aws",
        "region": "us-east-1",
        "instance_type": "t3.large",
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(custom_config, f)
        tmp_path = f.name

    try:
        config = handler.load_config(tmp_path)
        assert config["region"] == "us-east-1"
        assert config["instance_type"] == "t3.large"
    finally:
        os.unlink(tmp_path)


def test_default_config_has_required_keys(handler):
    config = handler.load_config("nonexistent.yaml")
    assert "cloud_provider" in config
    assert "region" in config
    assert "instance_type" in config


def test_default_region_is_india(handler):
    config = handler.load_config("nonexistent.yaml")
    assert config["region"] == "ap-south-1"
