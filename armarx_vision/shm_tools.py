import os
import numpy as np
import mmap
from armarx_core.config import config


def path_to_shm(provider_name: str) -> str:
    if not config.getboolean("Misc", "python_shm_support", fallback=False):
        return None
    username = os.getlogin()
    shm_file = f"/dev/shm/{provider_name}MemoryImageProvider{username}"
    if os.path.isfile(shm_file):
        return shm_file
    return None


def read_images_shm(shm_file: str, data_dimensions):
    image_size = np.prod(data_dimensions)
    shm_size = image_size + 1024 + 128
    with open(shm_file) as f:
        with mmap.mmap(f.fileno(), length=shm_size, access=mmap.ACCESS_READ) as m:
            data = m.read()

    image = np.frombuffer(data, dtype=np.uint8)
    image = image[696:]
    image = image[:image_size]
    image = image.reshape(data_dimensions)

    return image
