from pathlib import Path
import logging
from Controllers.ConfigController import (
    ConfigController,
)


class OBSInfoTool:

    def update_show_info(
        self, profile_dir, config_file="twitch_channel.yaml", config_group="info"
    ):
        texts_dir = Path(profile_dir) / "obs_texts"
        texts_dir.mkdir(exist_ok=True)

        file_config_keys = {
            "title.txt": "series",
            "episode.txt": "episode",
            "genre.txt": "genre",
        }

        config = ConfigController.get_config_file(config_file)

        for file_name, config_key in file_config_keys.items():
            current_value = config[config_group][config_key]
            print(f"Current {config_key.capitalize()}: {current_value}")
            new_value = input(
                f"Enter new {config_key.capitalize()} (press Enter to skip): "
            ).strip()

            if new_value:
                config[config_group][config_key] = new_value
                ConfigController.update_config_file(
                    config_file, config_group, config_key, new_value
                )

        for file_name, config_key in file_config_keys.items():
            file_path = texts_dir / file_name
            new_value = config[config_group][config_key]
            if config_key == "series":
                new_value = self.combine_series_and_episode(
                    config[config_group]["series"], config[config_group]["episode"]
                )
            self.update_obs_text(file_path, new_value)

    def combine_series_and_episode(self, series, episode):
        return f"{series} #{episode}"

    def update_obs_text(self, file_path, new_value):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(new_value))
