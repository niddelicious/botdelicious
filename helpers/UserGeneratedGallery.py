import os
import random
from Helpers.Dataclasses import UserGeneratedImage


class UserGeneratedGallery:
    _folder_path = rf"C:\Users\micro\Pictures\SD Chat\Original"
    _pool = []
    _played = []
    _max_pool_size = 0

    def __init__(self):
        if not UserGeneratedGallery._pool:
            UserGeneratedGallery._populate_pool()

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
                cls._pool.append(UserGeneratedImage(i, filename, name))

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
    usergenerated_gallery = UserGeneratedGallery()
    for _ in range(usergenerated_gallery.max_pool_size):
        image = usergenerated_gallery.get_random_image()
        print(
            f"Image {image.index + 1} out of {usergenerated_gallery.max_pool_size}: {image.name} - {image.filename}"
        )
        print(f"Current pool size: {usergenerated_gallery.current_pool_size}")
        print(f"Current played size: {usergenerated_gallery.current_played_size}")
