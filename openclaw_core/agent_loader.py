import yaml
import os


def load_agent_config(agent_path):
    config_path = os.path.join(agent_path, "config", "astra_config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found at {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)
