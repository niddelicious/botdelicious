import asyncio
from Helpers.MidjourneyGallery import MidjourneyGallery
from Helpers.Dataclasses import MidjourneyImage
from Modules.OBSModule import OBSModule


class MidjourneySlideshow:
    def __init__(self, obs_instance: OBSModule):
        self.obs_instance = obs_instance
        self._gallery = MidjourneyGallery()
        self._current_layer = "A"
        self._default_timer = 12
        self._default_fade = 2
        self._default_delay = 8
        self._pool_size = self._gallery.max_pool_size

    def get_next_image(self) -> MidjourneyImage:
        return self._gallery.get_random_image()

    async def new_image(self, layer: str = "A"):
        image = self.get_next_image()
        title = f"{image.name} ({image.index + 1} out of {self._pool_size})"
        await asyncio.gather(
            self.obs_instance.call_update_image(
                input_name=f"Midjourney Image {layer}",
                input_source=image.filename,
            ),
            self.obs_instance.call_update_text(
                input_name=f"Midjourney Text {layer}",
                text=title,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name=f"Reset Zoom {layer}",
                filter_enabled=True,
            ),
        )

    async def play_a(self):
        await asyncio.gather(
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Zoom In A",
                filter_enabled=True,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Fade In A",
                filter_enabled=True,
            ),
        )

    async def play_b(self):
        await asyncio.gather(
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Zoom In B",
                filter_enabled=True,
            ),
        )

    async def fade_out_a(self):
        await self.obs_instance.call_toggle_filter(
            source_name="Screen: Midjourney",
            filter_name="Fade Out A",
            filter_enabled=True,
        )

    async def reset_all(self):
        await asyncio.gather(
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Zoom In A",
                filter_enabled=False,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Zoom In B",
                filter_enabled=False,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Fade In A",
                filter_enabled=False,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Fade In B",
                filter_enabled=False,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Fade Out A",
                filter_enabled=False,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Fade Out B",
                filter_enabled=False,
            ),
        )
        await asyncio.gather(
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Reset Zoom A",
                filter_enabled=True,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Reset Zoom B",
                filter_enabled=True,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Reset Fade A",
                filter_enabled=True,
            ),
            self.obs_instance.call_toggle_filter(
                source_name="Screen: Midjourney",
                filter_name="Reset Fade B",
                filter_enabled=True,
            ),
        )

    async def slideshow_loop(self):
        await self.reset_all()
        await self.new_image("A")
        while True:
            await self.play_a()
            await asyncio.sleep(self._default_fade)
            await self.new_image("B")
            await asyncio.sleep(self._default_delay)
            await self.play_b()
            await self.fade_out_a()
            await asyncio.sleep(self._default_fade)
            await self.new_image("A")
            await asyncio.sleep(self._default_delay)
