from pathlib import Path
import yaml
from dotmap import DotMap


class ConfigController:
    _config = None
    _config_file = Path("config.yml")

    @classmethod
    def update_config(cls, group, setting, value):
        with cls._config_file.open("r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        config[group][setting] = value

        with cls._config_file.open("w") as config_file:
            yaml.dump(config, config_file)
        cls._config[group][setting] = value

    @classmethod
    def get_config(cls):
        with cls._config_file.open("r") as config_file:
            cls._config = DotMap(
                yaml.load(config_file, Loader=yaml.FullLoader)
            )

    @classmethod
    def get(cls, config_name):
        if hasattr(cls._config, config_name):
            return getattr(cls._config, config_name)
        else:
            return False
