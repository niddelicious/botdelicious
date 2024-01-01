import asyncio
import random
from Helpers.UserGeneratedGallery import UserGeneratedGallery
from Helpers.Dataclasses import UserGeneratedImage
from Modules.OBSModule import OBSModule


class UserGeneratedSlideshow:
    def __init__(self, obs_instance: OBSModule):
        self.obs_instance = obs_instance
        self._gallery = UserGeneratedGallery()
        self._layers = ["A", "B", "C", "D", "E", "F"]
        self._last_layer = random.choice(self._layers)
        self._default_timer = 5
        self._pool_size = self._gallery.max_pool_size

    def get_next_image(self) -> UserGeneratedImage:
        return self._gallery.get_random_image()

    def get_next_layer(self) -> str:
        layer_list = self._layers.copy()
        layer_list.remove(self._last_layer)
        return random.choice(layer_list)

    async def new_image(self):
        image = self.get_next_image()
        layer = self.get_next_layer()
        self._last_layer = layer
        await self.obs_instance.call_toggle_filter(
            source_name=f"UG-{layer}",
            filter_name=f"Flash",
            filter_enabled=True,
        )
        await self.obs_instance.call_update_usergallery_image(
            input_name=f"UG-{layer}",
            input_source=image.filename,
        )

    async def slideshow_loop(self):
        while True:
            await self.new_image()
            await asyncio.sleep(self._default_timer)
