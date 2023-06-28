import os
import random
from Helpers.Dataclasses import MidjourneyImage


class MidjourneyGallery:
    _folder_path = rf"C:\Users\micro\Pictures\Midjourney\1920x1080"
    _pool = []
    _played = []
    _max_pool_size = 0

    def __init__(self):
        if not MidjourneyGallery._pool:
            MidjourneyGallery._populate_pool()

    @classmethod
    def _populate_pool(cls):
        filenames = os.listdir(cls._folder_path)
        filenames.sort(
            key=lambda x: os.path.getmtime(os.path.join(cls._folder_path, x))
        )
        cls._max_pool_size = len(filenames)
        for i, filename in enumerate(filenames):
            if os.path.isfile(os.path.join(cls._folder_path, filename)):
                name = filename.split("_")[1:-1]
                name = " ".join(name).title()
                if len(name) > 49:
                    name = name[:50].rstrip() + "..."
                cls._pool.append(MidjourneyImage(i, filename, name))

    @classmethod
    def get_random_image(cls):
        if not cls._pool:
            cls._pool, cls._played = (
                cls._played,
                cls._pool,
            )  # Swap pool and played when pool is empty
        selected_image = random.choice(cls._pool)
        cls._pool.remove(selected_image)
        cls._played.append(selected_image)
        return selected_image

    @property
    def max_pool_size(self):
        return self._max_pool_size

    @property
    def current_pool_size(self):
        return len(self._pool)

    @property
    def current_played_size(self):
        return len(self._played)


if __name__ == "__main__":
    midjourney_gallery = MidjourneyGallery()
    for _ in range(midjourney_gallery.max_pool_size):
        image = midjourney_gallery.get_random_image()
        print(
            f"Image {image.index + 1} out of {midjourney_gallery.max_pool_size}: {image.name} - {image.filename}"
        )
        print(f"Current pool size: {midjourney_gallery.current_pool_size}")
        print(f"Current played size: {midjourney_gallery.current_played_size}")
