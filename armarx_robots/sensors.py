from functools import lru_cache

from visionx import ImageProviderInterfacePrx
from visionx import ReferenceFrameInterfacePrx

from armarx_vision.camera_utils import get_stereo_calibration
from armarx_vision.camera_utils import get_calibration
from armarx_vision.image_utils import read_images

class Camera:

    def __init__(self, name):
        self.provider_name = name
        self.images = property(lambda self: read_images(name))

    @property
    @lru_cache(1)
    def info(self):
        proxy = ImageProviderInterfacePrx.get_proxy(self.provider_name)
        image_format = proxy.getImageFormat()
        image_format = proxy.getImageFormat()
        width = image_format.dimension.width
        height = image_format.dimension.height

        proxy = ImageProviderInterfacePrx.get_proxy(self.provider_name)
        number_of_images = proxy.getNumberImages()

        return {'proxy': proxy, 'width': width, 'height': height, 'num_images':
                number_of_images}


    @property
    @lru_cache(1)
    def reference_frame_name(self):
        proxy = ReferenceFrameInterfacePrx.get_proxy(self.provider_name)
        return proxy.getReferenceFrame()

    @property
    @lru_cache(1)
    def num_images(self):
        proxy = ImageProviderInterfacePrx.get_proxy(self.provider_name)
        return proxy.getNumberImages()

    @property
    @lru_cache(1)
    def calibration(self):
        if self.num_images == 2:
            return get_stereo_calibration(self.provider_name)
        else:
            return get_calibration(self.provider_name)

