from functools import lru_cache

from visionx import ImageProviderInterfacePrx

from armarx_vision.camera_utils import get_stereo_calibration
from armarx_vision.camera_utils import get_calibration
from armarx_vision.image_utils import read_images

from visionx import ImageFormatInfo
from visionx import ReferenceFrameInterfacePrx
from functools import partial

from typing import Any
from typing import Dict

class Camera:
    """
    Convenience class for accessing the camera information and images 
    """
    def __init__(self, name):
        self.provider_name = name
        self.images = partial(read_images, name)

    @property
    @lru_cache(1)
    def proxy(self):
        """
        Returns the proxy of the visionx.ImageProvider
        """
        return ImageProviderInterfacePrx.get_proxy(self.provider_name)

    @property
    def image_format(self) -> ImageFormatInfo:
        return self.proxy.getImageFormat()

    @property
    def info(self) -> Dict[str, Any]:
        """
        Returns camera information such as width, height of the image 
        """
        proxy = self.proxy
        image_format = proxy.getImageFormat()
        width = image_format.dimension.width
        height = image_format.dimension.height

        proxy = ImageProviderInterfacePrx.get_proxy(self.provider_name)
        number_of_images = proxy.getNumberImages()

        return {
            "proxy": proxy,
            "width": width,
            "height": height,
            "num_images": number_of_images,
        }

    @property
    @lru_cache(1)
    def reference_frame_name(self):
        """
        Returns the frame the camera images are reported in
        """
        proxy = ReferenceFrameInterfacePrx.get_proxy(self.provider_name)
        return proxy.getReferenceFrame()

    @property
    @lru_cache(1)
    def num_images(self):
        """
        Returns the number of images
        """
        return self.proxy.getNumberImages()

    @property
    @lru_cache(1)
    def calibration(self):
        """
        Returns the camera calibration matrix
        """
        if self.num_images == 2:
            return get_stereo_calibration(self.provider_name)
        else:
            return get_calibration(self.provider_name)
