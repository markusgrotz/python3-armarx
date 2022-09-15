import numpy as np

from .import_aron_slice import import_aron_slice


dtype_rgb = [("r", "i1"), ("g", "i1"), ("b", "i1")]

dtypes_dict = {
    "float": np.float32,
    "float32": np.float32,
    "double": np.float64,
    "float64": np.float64,
    "16": dtype_rgb,  # "16" == OpenCV 8UC3 = RGB image
    # "16": np.float32,  # "16" == OpenCV F1C1 = Depth image
}


def convert_dtype_rgb_to_int8(array: np.ndarray) -> np.ndarray:
    """
    Converts an array with shape (m, n) and dtype dtype_rgb
    to an array with shape (m, n, 3) and dtype int8.

    :param array: The RGB image with structured dtype.
    :return: The RGB image with native dtype.
    """
    return np.stack([array[c] for c in "rgb"], axis=-1)


try:
    # beta 0.2.3
    class AronIceTypes:
        ARON_VERSION = "beta 0.2.3"

        ns = import_aron_slice().data.dto

        Data = ns.GenericData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.List
        Dict = ns.Dict

        NDArray = ns.NDArray

        @classmethod
        def string(cls, value: str) -> String:
            return cls.String(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def bool(cls, value: int) -> Bool:
            return cls.Bool(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def int(cls, value: int) -> Int:
            return cls.Int(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def long(cls, value: int) -> Long:
            return cls.Long(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def float(cls, value: float) -> Float:
            return cls.Float(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def list(cls, elements: list) -> List:
            return cls.List(elements=elements, VERSION=cls.ARON_VERSION)

        @classmethod
        def dict(cls, elements: dict) -> Dict:
            return cls.Dict(elements=elements, VERSION=cls.ARON_VERSION)

except AttributeError as e:
    # < 0.2.3

    class AronIceTypes:

        ns = import_aron_slice().data

        Data = ns.AronData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.AronList
        Dict = ns.AronDict

        NdArray = ns.AronNDArray
