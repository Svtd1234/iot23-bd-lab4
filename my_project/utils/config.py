import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CONFIG_PATH = os.path.join(BASE_DIR, "config", "app.yml")

ENV_OVERRIDES = {
    "DB_DRIVER": "driver",
    "DB_HOST": "host",
    "DB_PORT": "port",
    "DB_USER": "user",
    "DB_PASSWORD": "password",
    "DB_NAME": "name",
    "DB_SQLITE_PATH": "sqlite_path",
}


def load_config(path=DEFAULT_CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    config.setdefault("flask", {})
    config.setdefault("database", {})
    for env_name, key in ENV_OVERRIDES.items():
        value = os.environ.get(env_name)
        if value is not None:
            config["database"][key] = int(value) if key == "port" else value
    return config
