import yaml
from dotmap import DotMap


class ConfigManager:
    def __init__(self, parent=None):
        self.parent = parent

    def updateConfig(self, group, setting, value):
        with open("config.yml") as configFile:
            config = yaml.load(configFile, Loader=yaml.FullLoader)

        config[group][setting] = value

        with open("config.yml", "w") as configFile:
            yaml.dump(config, configFile)
        self.getConfig()

    def getConfig(self):
        with open("config.yml", "r") as config:
            self.parent.config = DotMap(yaml.load(config, Loader=yaml.FullLoader))
