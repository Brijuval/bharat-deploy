import os
from typing import Dict

import yaml


class ConfigHandler:
    DEFAULT_CONFIG: Dict = {
        "cloud_provider": "aws",
        "region": "ap-south-1",
        "instance_type": "t3.micro",
        "tags": {
            "project": "bharat-deploy",
            "environment": "dev",
        },
    }

    def load_config(self, config_path: str = "config/bharat.yaml") -> Dict:
        """Load configuration from a YAML file.

        Falls back to :attr:`DEFAULT_CONFIG` when the file does not exist.
        """
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    return loaded
        return dict(self.DEFAULT_CONFIG)
