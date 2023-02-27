import yaml
from dotmap import DotMap


class ConfigManager:
    _config = None

    def __new__(cls) -> None:
        cls.get_config()

    @classmethod
    def update_config(cls, group, setting, value):
        with open("config.yml") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        config[group][setting] = value

        with open("config.yml", "w") as config_file:
            yaml.dump(config, config_file)
        cls.get_config()

    @classmethod
    def get_config(cls):
        with open("config.yml", "r") as config_file:
            cls._config = DotMap(
                yaml.load(config_file, Loader=yaml.FullLoader)
            )

    @classmethod
    def get(cls, config_name):
        if cls._config[config_name]:
            return cls._config[config_name]
        else:
            return False
