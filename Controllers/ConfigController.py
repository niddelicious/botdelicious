from pathlib import Path
import yaml
from dotmap import DotMap


class ConfigController:
    _config = None
    _config_base_path = Path(".")

    @classmethod
    def set_config_base_path(cls, path):
        cls._config_base_path = Path(path)

    @classmethod
    def _get_config_file_path(cls, filename="config.yml"):
        return cls._config_base_path / filename

    @classmethod
    def update_config(cls, group, setting, value):
        config_file_path = cls._get_config_file_path()
        with config_file_path.open("r", encoding="utf-8") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        config[group][setting] = value

        with config_file_path.open("w", encoding="utf-8") as config_file:
            yaml.dump(config, config_file, allow_unicode=True)
        cls._config[group][setting] = value

    @classmethod
    def get_config(cls) -> DotMap:
        config_file_path = cls._get_config_file_path()
        with config_file_path.open("r", encoding="utf-8") as config_file:
            cls._config = DotMap(yaml.load(config_file, Loader=yaml.FullLoader))

    @classmethod
    def get(cls, config_name):
        if hasattr(cls._config, config_name):
            return getattr(cls._config, config_name)
        else:
            return False

    @classmethod
    def get_config_file(cls, filename):
        """Fetch and return a configuration as a DotMap from a specific file"""
        config_file_path = cls._get_config_file_path(filename)
        if not config_file_path.exists():
            raise FileNotFoundError(f"Config file {config_file_path} does not exist.")

        with config_file_path.open("r", encoding="utf-8") as config_file:
            return DotMap(yaml.load(config_file, Loader=yaml.FullLoader))

    @classmethod
    def update_config_file(cls, filename, group, setting, value):
        """Update a configuration setting in a specific file."""
        config_file_path = cls._get_config_file_path(filename)
        with config_file_path.open("r", encoding="utf-8") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        if group in config and setting in config[group]:
            config[group][setting] = value
        else:
            raise KeyError(
                f"Config group '{group}' or setting '{setting}' not found in {filename}."
            )

        with config_file_path.open("w", encoding="utf-8") as config_file:
            yaml.dump(config, config_file, allow_unicode=True)
        if cls._config and str(config_file_path) == str(cls._get_config_file_path()):
            cls._config[group][setting] = value
