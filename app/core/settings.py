import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

DEFAULT_CONFIG = {
    "poll_interval": 1,
    "max_retries": 3,
    "backoff_base": 2,
}


class Settings:

    def __init__(self):

        if not CONFIG_PATH.exists():

            with open(CONFIG_PATH, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)

        self.reload()

    def reload(self):

        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)

    def save(self):

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):

        return self.config[key]

    def set(self, key, value):

        self.config[key] = value
        self.save()